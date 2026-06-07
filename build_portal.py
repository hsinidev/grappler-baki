import os
import re
import shutil
import json
from datetime import datetime

# Global Chapter Registry for the Search/Dropdown
CHAPTER_REGISTRY = []

GA_TRACKING_ID = "G-32THHV9JQF"

FOOTER_LINKS_HTML = """
<div class="flex flex-wrap justify-center gap-6 mt-12 mb-8">
    <a href="about.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">About Us</a>
    <a href="contact.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">Contact</a>
    <a href="privacy-policy.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">Privacy Policy</a>
    <a href="dmca.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">DMCA</a>
    <a href="terms-of-service.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">Terms of Service</a>
    <a href="cookies-policy.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">Cookies Policy</a>
    <a href="disclaimer.html" class="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition">Disclaimer</a>
</div>
<p class="text-[10px] text-white/20 uppercase tracking-[0.1em] font-bold">&copy; 2024 Bakidou.org - All Rights Reserved.</p>
"""

KINETIC_HEADER_JS = """
<div id="kinetic-blade-container" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:0; pointer-events:none; opacity:0.6;"></div>
<script>
(function() {{
    const container = document.getElementById('kinetic-blade-container');
    if(!container) return;
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.PlaneGeometry(20, 10, 120, 120);
    const material = new THREE.ShaderMaterial({{
        transparent: true,
        uniforms: {{
            uTime: {{ value: 0 }},
            uColor: {{ value: new THREE.Color(getComputedStyle(document.documentElement).getPropertyValue('--primary').trim()) }}
        }},
        vertexShader: `
            varying vec2 vUv;
            uniform float uTime;
            void main() {{
                vUv = uv;
                vec3 pos = position;
                
                // Physical "Folded" Blade Effect
                float fold = abs(fract(pos.x * 0.5 + uTime * 0.1) - 0.5) * 2.0;
                float pleats = sin(pos.x * 10.0 + uTime * 2.0) * 0.05;
                
                pos.z += fold * 0.5;
                pos.z += pleats;
                pos.y += sin(pos.x * 0.5 + uTime) * 0.2;
                
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }}
        `,
        fragmentShader: `
            varying vec2 vUv;
            uniform vec3 uColor;
            uniform float uTime;
            void main() {{
                float scanline = sin(vUv.y * 200.0 - uTime * 20.0) * 0.15;
                float edge = step(0.1, abs(sin(vUv.x * 2.0 + uTime))); // Hard edges like a blade
                float alpha = (1.0 - smoothstep(0.48, 0.52, abs(vUv.y - 0.5))) * 0.4;
                vec3 color = uColor + scanline;
                gl_FragColor = vec4(color, alpha * edge);
            }}
        `,
        side: THREE.DoubleSide
    }});

    const mesh = new THREE.Mesh(geometry, material);
    mesh.rotation.x = -Math.PI / 4;
    mesh.position.y = 2;
    scene.add(mesh);

    camera.position.z = 5;

    function animate(t) {{
        requestAnimationFrame(animate);
        material.uniforms.uTime.value = t * 0.001;
        renderer.render(scene, camera);
    }}
    
    window.addEventListener('resize', () => {{
        camera.aspect = container.offsetWidth / container.offsetHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.offsetWidth, container.offsetHeight);
    }});
    
    animate(0);
}}();
</script>
"""

PORTAL_CONFIG = {
    "Grappler Baki": {
        "file": "index.html",
        "manga_dir": "grappler-baki",
        "colors": {
            "primary": "#cccccc",
            "accent": "#444444",
            "bg": "#111111"
        },
        "hero_desc": "Experience the brutal origin of the underground arena.",
        "shimmer": "radial-gradient(circle at 20% 30%, rgba(200,200,200,0.2) 0%, transparent 50%)",
        "hover_color": "#ffffff",
        "title_class": "title-brutalist",
        "bg_img": "assets/grappler-baki-hero.png",
        "favicon": "assets/grappler-baki-favicon.png"
    },
    "Baki": {
        "file": "baki.html",
        "manga_dir": "baki",
        "colors": {
            "primary": "#2e4a2b",
            "accent": "#1a1c1a",
            "bg": "#0a0a0a"
        },
        "hero_desc": "The ultimate showdown with the five death row convicts.",
        "shimmer": "radial-gradient(circle at 20% 30%, rgba(46,74,43,0.3) 0%, transparent 50%)",
        "hover_color": "#3cb371",
        "title_class": "title-gritty",
        "bg_img": "assets/baki-hero.png",
        "favicon": "assets/baki-favicon.png"
    },
    "Baki - Son Of Ogre": {
        "file": "son-of-ogre.html",
        "manga_dir": "baki-son-of-ogre",
        "colors": {
            "primary": "#dc143c",
            "accent": "#ffd700",
            "bg": "#1a0505"
        },
        "hero_desc": "The legendary battle between father and son. Demon Back unleashed.",
        "shimmer": "radial-gradient(circle at 20% 30%, rgba(220,20,60,0.4) 0%, transparent 50%)",
        "hover_color": "#ff4500",
        "title_class": "title-intensity",
        "bg_img": "assets/son-of-ogre-hero.png",
        "favicon": "assets/son-of-ogre-favicon.png"
    },
    "Baki-Dou (2018)": {
        "file": "baki-dou-2018.html",
        "manga_dir": "baki-dou-2018",
        "colors": {
            "primary": "#00bfff",
            "accent": "#2f4f4f",
            "bg": "#0f171e"
        },
        "hero_desc": "The sword-saint Musashi Miyamoto enters the modern era.",
        "shimmer": "radial-gradient(circle at 20% 30%, rgba(0,191,255,0.3) 0%, transparent 50%)",
        "hover_color": "#00ffff",
        "title_class": "title-sharp",
        "bg_img": "assets/baki-dou-hero.png",
        "favicon": "assets/baki-dou-favicon.png"
    },
    "Golden Kamui": {
        "file": "golden-kamui.html",
        "manga_dir": "golden-kamui",
        "colors": {
            "primary": "#fffafa",
            "accent": "#8b4513",
            "bg": "#0a1f11"
        },
        "hero_desc": "A desperate hunt for hidden gold in the frozen North.",
        "shimmer": "radial-gradient(circle at 20% 30%, rgba(255,250,250,0.2) 0%, transparent 50%)",
        "hover_color": "#ffd700",
        "title_class": "title-wilderness",
        "bg_img": "assets/golden-kamui-hero.png",
        "favicon": "assets/golden-kamui-favicon.png"
    }
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

READER_TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chapter_name} - {series_name} Chapter {chapter_id} Full Screen HD</title>
    <link rel="icon" type="image/png" href="../../../{favicon}">
    <meta name="description" content="Read {series_name} Chapter {chapter_id} Online in High Definition. Full-screen immersive reader with fast AVIF loading.">
    
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag.js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/three.min.js"></script>
    <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
    <style>
        body {{ background: #000; color: #fff; margin: 0; padding: 0; overflow-x: hidden; }}
        
        /* Custom Neon Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #000; }}
        ::-webkit-scrollbar-thumb {{ background: var(--primary); box-shadow: 0 0 10px var(--primary); }}
        
        /* Reading Progress Bar */
        #progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 4px;
            background: var(--primary);
            box-shadow: 0 0 15px var(--primary);
            z-index: 9999;
            transition: width 0.1s ease;
        }}

        .reader-image-container {{
            width: 100vw;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .reader-image-container img {{
            width: 100%;
            max-width: 100vw;
            height: auto;
            display: block;
            margin: 0;
        }}
        .sticky-nav {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            padding: 0.75rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.3s ease;
        }}
        .sticky-nav:hover {{ transform: translateY(0) !important; }}

        /* Custom Searchable Dropdown */
        .global-selector-btn {{
            background: rgba(255,255,255,0.05);
            border: 2px solid rgba(255,255,255,0.2);
            padding: 0.6rem 1.5rem;
            border-radius: 0;
            display: flex;
            align-items: center;
            gap: 1rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .global-selector-btn:hover {{ 
            border-color: #fff;
            background: rgba(255,255,255,0.1);
        }}
        
        .nav-btn {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            font-size: 0.65rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .nav-btn:hover {{
            background: #fff;
            color: #000;
            border-color: #fff;
        }}

        .reader-nav-btn {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
            padding: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .reader-nav-btn:hover {{
            background: var(--primary);
            border-color: var(--primary);
            color: #000;
            box-shadow: 0 0 15px var(--primary);
        }}
        
        .dropdown-menu {{
            display: none;
            position: absolute;
            top: calc(100% + 15px);
            right: 0;
            width: 380px;
            background: #0a0a0a;
            border: 2px solid #fff;
            box-shadow: 25px 25px 0px rgba(0,0,0,0.8);
            z-index: 1010;
            padding: 0;
            overflow: hidden;
        }}
        .dropdown-menu.active {{ display: block; animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .dropdown-header {{
            padding: 1.5rem;
            background: rgba(255,255,255,0.03);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .search-container {{
            position: relative;
            margin-bottom: 1rem;
        }}
        .search-container svg {{
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0.5;
            color: var(--primary);
        }}
        
        #node-search {{
            background: rgba(255,255,255,0.05);
            border: 2px solid rgba(255,255,255,0.1);
            width: 100%;
            padding: 1rem 1rem 1rem 3.5rem;
            border-radius: 0;
            color: #fff;
            font-size: 0.95rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
        }}
        #node-search::placeholder {{
            color: rgba(255,255,255,0.3);
            font-weight: 900;
        }}
        #node-search:focus {{
            outline: none;
            border-color: #fff;
            background: rgba(255,255,255,0.12);
            box-shadow: 0 0 30px rgba(255,255,255,0.1);
            padding-left: 4rem;
        }}
        .search-icon {{
            position: absolute;
            left: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255,255,255,0.3);
            pointer-events: none;
            transition: all 0.3s;
        }}
        #node-search:focus + .search-icon {{
            color: #fff;
            left: 1.5rem;
        }}

        .node-section-title {{
            font-size: 0.7rem;
            font-weight: 900;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.3em;
            padding: 1.25rem 1.5rem 0.75rem;
            opacity: 0.5;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 0.5rem;
        }}

        .series-grid {{
            padding: 0.5rem 1rem;
            display: grid;
            grid-template-columns: 1fr;
            gap: 4px;
        }}
        
        .series-link {{
            display: block;
            padding: 0.8rem 1.2rem;
            color: rgba(255, 255, 255, 0.5);
            font-size: 10px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 2px solid transparent;
            text-decoration: none;
            background: rgba(255,255,255,0.02);
        }}
        .series-link:hover {{
            color: white;
            background: rgba(255, 255, 255, 0.1);
            border-left-color: #fff;
            transform: translateX(5px);
        }}
        .series-link.active {{
            color: #fff;
            background: rgba(255, 255, 255, 0.15);
            border-left-color: #fff;
            pointer-events: none;
            box-shadow: inset 5px 0 15px rgba(255, 255, 255, 0.1);
        }}

        .node-list {{
            max-height: 350px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--primary) transparent;
        }}
        .node-item {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
            text-decoration: none;
        }}
        .node-item:hover {{ 
            background: rgba(255,255,255,0.05);
            padding-left: 2rem;
        }}
        .node-item .node-name {{
            font-size: 0.85rem;
            font-weight: 800;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}
        .node-item .node-id {{
            font-size: 0.7rem;
            color: var(--primary);
            font-weight: 900;
            background: rgba(255,255,255,0.05);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        /* SEO Content Section */
        .seo-section {{
            max-width: 900px;
            margin: 4rem auto;
            padding: 2rem;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            line-height: 1.8;
            color: rgba(255,255,255,0.8);
            font-size: 1.1rem;
        }}
        .seo-section h2 {{
            color: var(--primary);
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .seo-section p {{
            margin-bottom: 1.5rem;
        }}
        .seo-section strong {{
            color: #fff;
        }}
    </style>
    
    <!-- Programmatic SEO: ComicIssue Schema -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [{{
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://bakidou.org/"
      }},{{
        "@type": "ListItem",
        "position": 2,
        "name": "{series_name}",
        "item": "https://bakidou.org/{series_file}"
      }},{{
        "@type": "ListItem",
        "position": 3,
        "name": "{chapter_name}",
        "item": "https://bakidou.org/{current_url}"
      }}]
    }}
    </script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "ComicIssue",
      "name": "{chapter_name}",
      "issueNumber": "{chapter_id}",
      "about": "{series_name}",
      "publisher": {{
        "@type": "Organization",
        "name": "Bakidou"
      }},
      "image": "https://bakidou.org/{first_img}"
    }}
    </script>
</head>
<body class="antialiased">
    <div id="progress-bar"></div>
    <nav class="sticky-nav" id="sticky-nav">
        <div class="flex items-center gap-6">
            <a href="../../../{series_file}" class="text-xs font-black uppercase tracking-[0.2em] text-white/50 hover:text-white transition flex items-center gap-2">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                Portal
            </a>
            <div class="flex items-center gap-4">
                <span class="text-xs font-black tracking-widest uppercase text-[var(--primary)]">{series_name}</span>
                <div class="h-4 w-[1px] bg-white/10"></div>
                <span class="text-xs font-bold text-white/40">{chapter_name}</span>
            </div>
        </div>

        <div class="chapter-nav-center flex items-center gap-1">
            <button id="prev-btn" class="reader-nav-btn" title="Previous Chapter [Left Arrow]">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <div class="relative group">
                <button id="global-selector-btn" class="global-selector-btn">
                    <span class="text-[10px] font-black uppercase tracking-[0.2em] hidden md:block">Select Node</span>
                    <div class="w-2 h-2 bg-white/40 rounded-full animate-pulse shadow-[0_0_10px_rgba(255,255,255,0.5)]"></div>
                </button>

                <div id="dropdown-menu" class="dropdown-menu">
                    <div class="dropdown-header">
                        <div class="search-container">
                            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                            <input type="text" id="node-search" placeholder="Search {series_name} Chapters...">
                        </div>
                    </div>
                    
                    <div id="series-section">
                        <div class="node-section-title">Switch Portals</div>
                        <div class="series-grid">
                            {{SERIES_LINKS}}
                        </div>
                    </div>

                    <div class="node-section-title">Chapter Nodes</div>
                    <div id="nodes-container" class="node-list">
                        {all_chapters_options}
                    </div>
                </div>
            </div>
            <button id="next-btn" class="reader-nav-btn" title="Next Chapter [Right Arrow]">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M9 18l6-6-6-6"/></svg>
            </button>
        </div>

        <div class="flex items-center gap-3">
            <button onclick="toggleFullScreen()" class="nav-btn hidden sm:block">F-SCN</button>
        </div>
    </nav>

    <div class="reader-image-container">
        {images_html}
    </div>

    <!-- SEO_CONTENT_INJECTION_POINT -->

    <footer class="py-20 px-6 text-center border-t border-white/5 bg-black">
        {footer_links}
    </footer>

    <script>
        // Auto-hide nav on scroll
        let lastScroll = 0;
        window.addEventListener('scroll', () => {{
            const nav = document.getElementById('sticky-nav');
            const currentScroll = window.pageYOffset;
            if (currentScroll > lastScroll && currentScroll > 100) {{
                nav.style.transform = 'translateY(-100%)';
            }} else {{
                nav.style.transform = 'translateY(0)';
            }}
            lastScroll = currentScroll;
        }});

        // Keyboard Navigation (Arrow Keys)
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') {{
                document.getElementById('prev-btn')?.click();
            }} else if (e.key === 'ArrowRight') {{
                document.getElementById('next-btn')?.click();
            }} else if (e.key === 'f' || e.key === 'F') {{
                toggleFullScreen();
            }}
        }});

        const selectorBtn = document.getElementById('global-selector-btn');
        const dropdown = document.getElementById('dropdown-menu');
        if(selectorBtn) {{
            selectorBtn.addEventListener('click', (e) => {{
                e.stopPropagation();
                dropdown.classList.toggle('active');
                trackEvent('navigation', 'open_dropdown', '{series_name}');
            }});
        }}
        document.addEventListener('click', () => dropdown?.classList.remove('active'));
        dropdown?.addEventListener('click', (e) => e.stopPropagation());

        // Search Logic
        const search = document.getElementById('node-search');
        if(search) {{
            search.addEventListener('input', (e) => {{
                const query = e.target.value.toLowerCase();
                const seriesSection = document.getElementById('series-section');
                
                if(query.length > 0) {{
                    seriesSection.style.display = 'none';
                }} else {{
                    seriesSection.style.display = 'block';
                }}

                document.querySelectorAll('.node-item').forEach(item => {{
                    const text = item.innerText.toLowerCase();
                    item.style.display = text.includes(query) ? 'flex' : 'none';
                }});
            }});
        }}

        // Navigation Button Logic
        const chaptersList = Array.from(document.querySelectorAll('#nodes-container .node-item'));
        const currentPath = window.location.pathname;
        let currentIdx = chaptersList.findIndex(c => c.getAttribute('href').includes(currentPath));
        
        document.getElementById('prev-btn')?.addEventListener('click', () => {{
            if(currentIdx < chaptersList.length - 1) {{
                window.location.href = chaptersList[currentIdx + 1].getAttribute('href');
            }}
        }});
        document.getElementById('next-btn')?.addEventListener('click', () => {{
            if(currentIdx > 0) {{
                window.location.href = chaptersList[currentIdx - 1].getAttribute('href');
            }}
        }});

        // Reading Progress Bar Lock
        window.addEventListener('scroll', () => {{
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            document.getElementById("progress-bar").style.width = scrolled + "%";
        }});

        // Virtual Pageview Tracking
        function trackEvent(category, action, label) {{
            if(typeof gtag === 'function') {{
                gtag('event', action, {{
                    'event_category': category,
                    'event_label': label
                }});
            }}
        }}

        // Full Screen Toggle
        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}
    </script>
</body>
</html>
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{series_name} Manga Online | Premium Portal</title>
    <link rel="icon" type="image/png" href="{favicon}">
    <meta name="description" content="Read free {series_name} Manga Online in HD quality. Access the latest chapters, volumes, and full archives of the legendary Baki universe. Safe and fast mobile reader.">
    
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag.js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>
    <script src="https://unpkg.com/@tailwindcss/browser@4" defer></script>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
        :root {{ 
            --primary: {primary_color}; 
            --primary-rgb: {primary_rgb};
            --accent: {accent_color}; 
            --accent-rgb: {accent_rgb};
            --bg: {bg_color};
            --hover-ignite: {hover_color};
            --bg-img: url('{bg_img}');
        }}
        body {{ 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            background: var(--bg); 
            color: #fff; 
            overflow-x: hidden; 
            scroll-behavior: smooth; 
        }}
        
        /* Custom Neon Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #000; }}
        ::-webkit-scrollbar-thumb {{ background: var(--primary); box-shadow: 0 0 10px var(--primary); }}

        .bangers {{ font-family: 'Bangers', cursive; }}
        
        /* Hero Identities */
        .hero-banner {{
            background-image: var(--bg-img);
            background-size: cover;
            background-position: center 25% !important; /* Locked for character visibility */
            background-attachment: fixed;
            position: relative;
            filter: contrast(1.1) brightness(0.9); /* Sharper, more dramatic look */
        }}
        
        @media (max-width: 768px) {{
            .hero-banner {{
                background-position: 25% center !important; /* Adjusted for mobile portrait */
            }}
        }}

        .hero-banner::before {{
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.4) 100%);
            z-index: 1;
        }}
        
        .hero-banner.ignite {{
            filter: brightness(1.3) contrast(1.1);
            transform: scale(1.05); /* Stronger pop on ignite */
        }}

        /* Sharp UI Overlay (No Blur for clarity) */
        .glass-overlay {{
            background: linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 70%, transparent 100%);
            border-left: 6px solid var(--primary);
            padding: 4rem 3rem;
            border-top: 1px solid rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        
        .hero-banner.ignite .glass-overlay {{
            background: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,0.8) 70%, transparent 100%);
            border-color: var(--hover-ignite);
            box-shadow: -20px 0 50px rgba(0,0,0,0.8);
        }}

        /* Dynamic Titles */
        .title-brutalist {{
            text-shadow: 4px 4px 0px #444, -2px -2px 0px #fff;
            animation: brutalShake 3s infinite;
        }}
        @keyframes brutalShake {{
            0%, 100% {{ transform: skew(0deg); }}
            50% {{ transform: skew(1deg); }}
        }}

        .title-gritty {{
            text-shadow: 2px 2px 10px #000;
            background: repeating-linear-gradient(45deg, #2e4a2b, #1a1c1a 10px);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .title-intensity {{
            text-shadow: 0 0 20px rgba(220,20,60,0.8);
            animation: bloodPulse 2s infinite alternate;
        }}
        @keyframes bloodPulse {{
            from {{ text-shadow: 0 0 10px red, 0 0 20px red; transform: scale(1); }}
            to {{ text-shadow: 0 0 20px red, 0 0 40px darkred; transform: scale(1.02); }}
        }}

        .title-sharp {{
            text-shadow: 0 0 5px #00ffff;
            animation: cyberGlow 1.5s infinite alternate;
        }}
        @keyframes cyberGlow {{
            from {{ filter: hue-rotate(0deg); }}
            to {{ filter: hue-rotate(20deg); text-shadow: 0 0 10px #00bfff, 0 0 20px #00bfff; }}
        }}

        .title-wilderness {{
            text-shadow: 0 0 40px rgba(var(--primary-rgb), 0.6), 0 0 80px rgba(0,0,0,0.5);
            letter-spacing: -0.02em;
            filter: drop-shadow(0 10px 10px rgba(0,0,0,0.8));
        }}
        @keyframes goldShimmer {{
            to {{ background-position: 200% center; }}
        }}

        /* Neon Glow behind title on Ignite */
        .hero-banner.ignite h1 {{
            filter: drop-shadow(0 0 15px var(--hover-ignite));
        }}

        .glass-card {{
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .glass-card img {{
            filter: grayscale(100%) brightness(0.5);
            transition: all 0.7s ease;
            image-rendering: -webkit-optimize-contrast;
            image-rendering: crisp-edges;
        }}
        .glass-card:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: var(--hover-ignite);
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 20px var(--hover-ignite);
        }}
        .glass-card:hover img {{
            filter: grayscale(0%) brightness(1);
            transform: scale(1.1);
            opacity: 1 !important;
        }}

        /* --- High Designed Blade Navigation --- */
        .blade-nav-link {{
            position: relative;
            padding: 0.6rem 0;
            color: rgba(255, 255, 255, 0.35);
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.4em;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: inline-block;
            text-decoration: none;
            overflow: visible;
        }}

        .blade-nav-link span {{
            display: inline-block;
            position: relative;
            z-index: 2;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), color 0.4s;
        }}

        .blade-nav-link.active {{
            color: var(--primary);
            letter-spacing: 0.5em;
        }}

        /* The Blade Edge */
        .blade-nav-link::before {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 0%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), #fff, var(--primary), transparent);
            box-shadow: 0 0 15px var(--primary);
            transition: width 0.6s cubic-bezier(0.23, 1, 0.32, 1);
            transform: skewX(-45deg);
        }}

        .blade-nav-link:hover {{
            color: #fff;
            filter: drop-shadow(0 0 8px rgba(var(--primary-rgb), 0.8));
        }}

        .blade-nav-link:hover span {{
            transform: scale(1.1) translateY(-2px);
        }}

        .blade-nav-link:hover::before {{
            width: 100%;
        }}

        /* The Folding Effect Overlay */
        .blade-nav-link::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--primary);
            opacity: 0;
            transform: scaleX(0);
            transform-origin: left;
            z-index: 1;
            mix-blend-mode: overlay;
        }}

        /* Kinetic Text Shadow for Blade links */
        .active.blade-nav-link {{
            text-shadow: 0 0 10px rgba(var(--primary-rgb), 0.5);
        }}

        @media (max-width: 1024px) {{
            .blade-nav-link {{
                margin: 0.5rem;
                letter-spacing: 0.2em;
            }}
        }}

        /* Global Selector Dropdown */
        .global-selector-btn {{
            background: #000;
            border: 2px solid rgba(255,255,255,0.2);
            padding: 0.6rem 1.5rem;
            border-radius: 0;
            display: flex;
            align-items: center;
            gap: 1rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .global-selector-btn:hover {{ 
            border-color: var(--primary);
            background: rgba(255,255,255,0.05);
        }}
        
        .dropdown-menu {{
            display: none;
            position: absolute;
            top: calc(100% + 15px);
            right: 0;
            width: 380px;
            background: #0a0a0a;
            border: 2px solid #fff;
            box-shadow: 25px 25px 0px rgba(0,0,0,0.8);
            z-index: 1010;
            padding: 0;
            overflow: hidden;
        }}
        .dropdown-menu.active {{ display: block; animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .dropdown-header {{
            padding: 1.5rem;
            background: rgba(255,255,255,0.03);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .search-container {{
            position: relative;
            margin-bottom: 1rem;
        }}
        .search-container svg {{
            position: absolute;
            left: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            opacity: 1;
            color: var(--primary);
            filter: drop-shadow(0 0 5px var(--primary));
        }}
        
        #node-search {{
            background: rgba(255,255,255,0.05);
            border: 2px solid rgba(255,255,255,0.2);
            width: 100%;
            padding: 0.85rem 1rem 0.85rem 3rem;
            border-radius: 0;
            color: #fff;
            font-size: 0.9rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            transition: all 0.3s;
        }}
        #node-search::placeholder {{
            color: rgba(255,255,255,0.4);
            font-weight: 900;
        }}
        #node-search:focus {{
            outline: none;
            border-color: var(--primary);
            background: rgba(255,255,255,0.1);
            box-shadow: 0 0 25px var(--primary);
        }}

        .node-section-title {{
            font-size: 0.7rem;
            font-weight: 900;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 0.3em;
            padding: 1.25rem 1.5rem 0.75rem;
            opacity: 0.8;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 0.5rem;
        }}

        .series-grid {{
            padding: 0.5rem 1rem;
            display: grid;
            grid-template-columns: 1fr;
            gap: 4px;
        }}
        
        .series-link {{
            display: block;
            padding: 0.8rem 1.2rem;
            color: rgba(255, 255, 255, 0.5);
            font-size: 10px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 2px solid transparent;
            text-decoration: none;
            background: rgba(255,255,255,0.02);
        }}
        .series-link:hover {{
            color: white;
            background: rgba(255, 255, 255, 0.1);
            border-left-color: var(--primary);
            transform: translateX(5px);
        }}
        .series-link.active {{
            color: var(--primary);
            background: rgba(var(--primary-rgb), 0.2);
            border-left-color: var(--primary);
            pointer-events: none;
            box-shadow: inset 5px 0 15px rgba(var(--primary-rgb), 0.1);
        }}

        .node-list {{
            max-height: 350px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--primary) transparent;
        }}
        .node-item {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
            text-decoration: none;
        }}
        .node-item:hover {{ 
            background: rgba(255,255,255,0.05);
            padding-left: 2rem;
        }}
        .node-item .node-name {{
            font-size: 0.85rem;
            font-weight: 800;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}
        .node-item .node-id {{
            font-size: 0.7rem;
            color: var(--primary);
            font-weight: 900;
            background: rgba(255,255,255,0.05);
            padding: 2px 6px;
            border-radius: 4px;
        }}
    </style>

    <script>
        document.addEventListener("DOMContentLoaded", () => {{
            const header = document.querySelector('header.hero-banner');
            if(header) {{
                header.addEventListener('mouseenter', () => header.classList.add('ignite'));
                header.addEventListener('mouseleave', () => header.classList.remove('ignite'));
            }}

            // Dropdown Logic
            const selectorBtn = document.getElementById('global-selector-btn');
            const dropdown = document.getElementById('dropdown-menu');
            if(selectorBtn) {{
                selectorBtn.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    dropdown.classList.toggle('active');
                    if(dropdown.classList.contains('active')) {{
                        if(typeof gtag === 'function') gtag('event', 'select_node_click', {{ 'event_category': 'navigation', 'series': '{series_name}' }});
                    }}
                }});
            }}
            document.addEventListener('click', () => dropdown?.classList.remove('active'));
            dropdown?.addEventListener('click', (e) => e.stopPropagation());

            // Search Logic
            const search = document.getElementById('node-search');
            if(search) {{
                search.addEventListener('input', (e) => {{
                    const query = e.target.value.toLowerCase();
                    const seriesSection = document.getElementById('series-section');
                    
                    if(query.length > 0) {{
                        seriesSection.style.display = 'none';
                    }} else {{
                        seriesSection.style.display = 'block';
                    }}

                    document.querySelectorAll('.node-item').forEach(item => {{
                        const text = item.innerText.toLowerCase();
                        item.style.display = text.includes(query) ? 'flex' : 'none';
                    }});
                }});
            }}

            // Blade Navigation & Title Orchestration (using animejs-animation skill)
            const navElements = document.querySelectorAll('.blade-nav-link');
            const mainTitle = document.querySelector('.hero-banner h1');
            
            // Staggered Unfold Animation
            const tl = anime.timeline({{
                easing: 'easeOutQuart',
                duration: 1200
            }});

            tl.add({{
                targets: '.blade-nav-link',
                opacity: [0, 1],
                translateX: [20, 0],
                rotateY: [90, 0],
                delay: anime.stagger(150, {{start: 500}}),
                begin: (anim) => {{
                    document.querySelector('nav').style.opacity = '1';
                }}
            }}).add({{
                targets: mainTitle,
                opacity: [0, 1],
                scale: [0.95, 1],
                rotateX: [20, 0],
                duration: 2000,
                easing: 'spring(1, 80, 10, 0)'
            }}, '-=1000');

            // Hover interactions for Blade Links
            navElements.forEach(link => {{
                link.addEventListener('mouseenter', () => {{
                    anime({{
                        targets: link.querySelector('span'),
                        skewX: [-15, 0],
                        duration: 400,
                        easing: 'easeOutElastic(1, .6)'
                    }});
                    
                    if(!link.classList.contains('active')) {{
                        anime({{
                            targets: link,
                            letterSpacing: ['0.4em', '0.6em'],
                            duration: 600
                        }});
                    }}
                }});

                link.addEventListener('mouseleave', () => {{
                    if(!link.classList.contains('active')) {{
                        anime({{
                            targets: link,
                            letterSpacing: ['0.6em', '0.4em'],
                            duration: 600
                        }});
                    }}
                }});
            }});
        }});
        
        function toggleArchiveSort(method) {{
            const grid = document.querySelector('.archive-grid');
            const items = Array.from(grid.children);
            if(method === 'LATEST') {{
                items.sort((a, b) => b.dataset.num - a.dataset.num);
            }} else {{
                items.sort((a, b) => a.dataset.num - b.dataset.num);
            }}
            grid.innerHTML = '';
            items.forEach(i => grid.appendChild(i));
        }}

        function showAllChapters() {{
            document.querySelectorAll('.chapter-hidden').forEach(c => c.classList.remove('hidden', 'chapter-hidden'));
            document.getElementById('show-more-btn').style.display = 'none';
            if(typeof gtag === 'function') gtag('event', 'show_more_chapters', {{ 'event_category': 'interaction', 'series': '{series_name}' }});
        }}
    </script>
</head>
<body class="antialiased">
    
    <nav class="fixed top-0 w-full z-[100] px-6 py-4 flex justify-between items-center bg-black border-b-2 border-white/10">
        <a href="index.html" class="text-2xl bangers uppercase tracking-tighter text-[var(--primary)]">Universe Controller</a>
        
        <div class="flex items-center gap-6">
            <div class="hidden lg:flex gap-6 items-center">
                {nav_links}
            </div>
            
            <div class="relative">
                <button id="global-selector-btn" class="global-selector-btn">
                    <span class="text-[10px] font-black uppercase tracking-[0.2em]">Select Node</span>
                    <div class="w-3 h-3 bg-[var(--primary)] rounded-full animate-pulse"></div>
                </button>
                
                <div id="dropdown-menu" class="dropdown-menu">
                    <div class="dropdown-header">
                        <div class="search-container">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square" stroke-linejoin="bevel"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                            <input type="text" id="node-search" placeholder="Search {series_name} Chapters...">
                        </div>
                    </div>
                    
                    <div id="series-section">
                        <div class="node-section-title">Switch Portals</div>
                        <div class="series-grid">
                            {{SERIES_LINKS}}
                        </div>
                    </div>

                    <div class="node-section-title">Chapter Nodes</div>
                    <div id="nodes-container" class="node-list">
                        {global_node_list}
                    </div>
                </div>
            </div>
        </div>
    </nav>
    
    <header class="relative hero-banner min-h-[95vh] flex flex-col justify-end pb-24 px-6 md:px-20 overflow-hidden">
        {kinetic_header}
        <!-- Overlay gradient to ensure text readability at the bottom -->
        <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80 z-2"></div>
        
        <!-- Foreground content -->
        <div class="relative z-10 max-w-5xl glass-overlay">
            <h1 class="text-8xl md:text-[8rem] bangers leading-none tracking-tighter uppercase mb-6 {title_class} transition-all duration-500">
                {series_name}
            </h1>
            <p class="text-xl md:text-2xl text-white/80 max-w-2xl font-bold uppercase tracking-widest mb-12 drop-shadow-[0_2px_4px_rgba(0,0,0,1)]">
                Part of the Universe. {hero_desc}
            </p>
            <div class="flex gap-6">
                <a href="#archive" class="px-12 py-5 bg-[var(--primary)] text-black bangers text-2xl uppercase tracking-widest hover:scale-105 transition" style="box-shadow: 0 0 20px var(--hover-ignite);">Enter Archive</a>
            </div>
        </div>
    </header>

    <main id="archive" class="relative z-20 py-20 px-6 md:px-20 max-w-[1400px] mx-auto min-h-screen">
        <div class="flex justify-between items-center mb-12">
            <h2 class="text-6xl bangers tracking-tighter uppercase">Archive / Records</h2>
            <div class="flex gap-4">
                <button onclick="toggleArchiveSort('LATEST')" class="px-6 py-2 bg-white/5 border border-white/10 hover:border-[var(--primary)] text-[10px] font-bold uppercase tracking-widest transition">Latest</button>
                <button onclick="toggleArchiveSort('OLDEST')" class="px-6 py-2 bg-white/5 border border-white/10 hover:border-[var(--primary)] text-[10px] font-bold uppercase tracking-widest transition">Oldest</button>
            </div>
        </div>
        
        <div class="archive-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {chapters_html}
        </div>

        <div id="show-more-btn" class="mt-12 text-center">
            <button onclick="showAllChapters()" class="px-20 py-6 bg-white/5 border border-white/10 hover:bg-white hover:text-black transition uppercase bangers text-2xl tracking-[0.2em]">Show More Records</button>
        </div>
    </main>

    <!-- SEO_CONTENT_INJECTION_POINT -->

    <footer class="relative z-20 py-20 px-6 text-center border-t border-white/5 bg-black">
        <div class="text-[10px] font-black uppercase tracking-[1em] text-white/20 mb-8 italic">Universe Network Protocol</div>
        {footer_links}
    </footer>
</body>
</html>
"""

def normalize_directories():
    print("Normalizing directories...")
    if not os.path.exists("manga"):
        return
        
    for name, config in PORTAL_CONFIG.items():
        original_dir = config["manga_dir"]
        series_slug = slugify(name)
        config["manga_slug"] = series_slug  # Save slug in config
        
        base_dir = os.path.join("manga", original_dir)
        slug_base_dir = os.path.join("manga", series_slug)
        
        # Resolve doubled folder if it exists (e.g. manga/Grappler Baki/Grappler Baki)
        doubled_dir = os.path.join(base_dir, original_dir)
        if os.path.exists(doubled_dir) and os.path.isdir(doubled_dir):
            print(f"Flattening doubled directory: {doubled_dir}")
            for item in os.listdir(doubled_dir):
                shutil.move(os.path.join(doubled_dir, item), os.path.join(base_dir, item))
            os.rmdir(doubled_dir)
            
        # Rename to slugified base directory if needed
        if os.path.exists(base_dir):
            if base_dir.lower() != slug_base_dir.lower():
                print(f"Renaming {base_dir} to {slug_base_dir}")
                try:
                    shutil.move(base_dir, slug_base_dir)
                except Exception as e:
                    print(f"Failed to move {base_dir} to {slug_base_dir}: {e}")
            else:
                # On Windows, if only case differs, moving is complex. 
                # We'll just continue using slug_base_dir for logic.
                pass

        # Normalize chapter directories
        if os.path.exists(slug_base_dir):
            for d in os.listdir(slug_base_dir):
                chap_path = os.path.join(slug_base_dir, d)
                if os.path.isdir(chap_path):
                    # Replace spaces and funny chars in chapter name
                    chap_slug = slugify(d)
                    target_chap_path = os.path.join(slug_base_dir, chap_slug)
                    
                    if chap_path.lower() != target_chap_path.lower():
                        print(f"Renaming chapter {chap_path} to {target_chap_path}")
                        try:
                            os.rename(chap_path, target_chap_path)
                            chap_path = target_chap_path
                        except OSError as e:
                            print(f"Failed to rename {chap_path}: {e}")

def generate_chapters(slug_base_dir, series_name, series_file):
    if not os.path.exists(slug_base_dir):
        return "<p class='col-span-full text-center'>No chapters found for this series yet.</p>"
    
    chapters = []
    print(f"Generating chapters for {series_name}...")
    for chap_slug in os.listdir(slug_base_dir):
        chap_path = os.path.join(slug_base_dir, chap_slug)
        if os.path.isdir(chap_path):
            # Support multiple image formats
            images = [img for img in os.listdir(chap_path) if img.lower().endswith(('.webp', '.jpg', '.jpeg', '.png'))]
            if images:
                def img_sort(x):
                    nums = re.findall(r'\d+', x)
                    return int(nums[0]) if nums else 0
                images.sort(key=img_sort)
                first_img = images[0]
                
                rel_base_dir = slug_base_dir.replace("\\", "/")
                img_path = f"{rel_base_dir}/{chap_slug}/{first_img}"
                index_path = f"{rel_base_dir}/{chap_slug}/index.html"
                
                match = re.search(r'\d+', chap_slug)
                num = float(match.group()) if match else 0
                
                chapters.append({
                    "slug": chap_slug,
                    "img": img_path,
                    "url": index_path,
                    "num": num,
                    "series": series_name,
                    "images": images,
                    "full_path": chap_path
                })
    
    # Sort for the build
    chapters.sort(key=lambda x: x["num"], reverse=True)
    
    # Register for global search
    for c in chapters:
        # Extract numeric part for a cleaner "Chapter ID" badge
        match = re.search(r'\d+', c['slug'])
        id_badge = match.group() if match else "?"
        CHAPTER_REGISTRY.append({
            "name": c['slug'].replace('-', ' ').title(), # No redundant series name in chapter title
            "id": id_badge,
            "url": c['url'],
            "series": series_name
        })
    
    html = ""
    for i, c in enumerate(chapters):
        display_name = c["slug"].replace("-", " ").title()
        hidden_class = "hidden chapter-hidden" if i >= 20 else ""
        
        html += f'''
        <a href="{c['url']}" data-num="{c['num']}" class="{hidden_class} glass-card group block relative overflow-hidden rounded-xl h-72 shadow-2xl">
            <img src="{c['img']}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-all duration-700" loading="lazy" decoding="async">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent"></div>
            <div class="absolute bottom-0 p-6 z-10 w-full">
                <div class="text-[10px] font-black tracking-widest text-[var(--primary)] uppercase mb-1">{series_name}</div>
                <h3 class="text-3xl bangers uppercase leading-none group-hover:translate-x-2 transition-transform text-white">{display_name}</h3>
            </div>
        </a>
        '''
        
    return html, chapters

def build_reader_pages(chapters, series_name, series_file, all_chapters_reg):
    # Filter chapters to only show ones from the CURRENT series for separation
    series_chapters = [c for c in all_chapters_reg if c["series"] == series_name]
    all_options = "".join([f'<a href="../../../{c["url"]}" class="node-item"><span class="node-name">{c["name"]}</span><span class="node-id">CH {c["id"]}</span></a>' for c in series_chapters])

    for c in chapters:
        display_name = c["slug"].replace("-", " ").title()
        # Full-page high-tech reader
        images_html = "\n        ".join([f'<img src="{img}" loading="lazy" decoding="async" class="w-full" alt="Page {i+1}">' for i, img in enumerate(c["images"])])
        
        match = re.search(r'\d+', c["slug"])
        chap_id = match.group() if match else c["slug"]

        # Build series links for reader with active state
        reader_series_links = ""
        for s_name in PORTAL_CONFIG.keys():
            is_active = "active" if s_name == series_name else ""
            filename = PORTAL_CONFIG[s_name]["file"]
            reader_series_links += f'<a href="../../../{filename}" class="series-link {is_active}">{s_name}</a>\n'

        # Preserve SEO content if it exists
        index_path = os.path.join(c["full_path"], "index.html")
        injected_seo = "<!-- SEO_CONTENT_INJECTION_POINT -->"
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "<!-- SEO_CONTENT_INJECTED -->" in content:
                    # Extract the entire injected section
                    start_marker = "<!-- SEO_CONTENT_INJECTED -->"
                    end_marker = "</section>"
                    start_idx = content.find(start_marker)
                    end_idx = content.find(end_marker, start_idx) + len(end_marker)
                    if start_idx != -1 and end_idx != -1:
                        injected_seo = content[start_idx:end_idx]

        reader_html = READER_TEMPLATE_HTML.format(
            series_file=series_file,
            images_html=images_html,
            all_chapters_options=all_options,
            ga_id=GA_TRACKING_ID,
            footer_links=FOOTER_LINKS_HTML,
            current_url=c["url"],
            first_img=c["img"],
            favicon=PORTAL_CONFIG[series_name]["favicon"],
            series_name=series_name,
            chapter_name=display_name,
            chapter_id=chap_id
        ).replace("<!-- SEO_CONTENT_INJECTION_POINT -->", injected_seo).replace("{{SERIES_LINKS}}", reader_series_links)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(reader_html)

def build_sites():
    normalize_directories()
    
    print("Scanning Series Content...")
    series_data = []
    for name, config in PORTAL_CONFIG.items():
        series_slug = config.get("manga_slug", slugify(name))
        slug_base_dir = os.path.join("manga", series_slug)
        chap_html, chapters = generate_chapters(slug_base_dir, name, config["file"])
        series_data.append((name, config, chap_html, chapters))

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"

    print("Building Portal Pages...")

    for name, config, chap_html, chapters in series_data:
        series_slug = config.get("manga_slug", slugify(name))
        
        # Build main navigation links with active state (Blade Designed)
        nav_links = "".join([
            f'<a href="{config["file"]}" class="blade-nav-link '
            f'{"active" if n == name else ""} ">'
            f'<span>{n}</span></a>'
            for n, config in PORTAL_CONFIG.items()
        ])
        
        # Series-specific node list for the homepage dropdown - separation logic
        series_node_list = "".join([f'<a href="{c["url"]}" class="node-item"><span class="node-name">{c["name"]}</span><span class="node-id">CH {c["id"]}</span></a>' for c in CHAPTER_REGISTRY if c["series"] == name])

        # Build series links with active state
        series_links_html = ""
        for s_name in PORTAL_CONFIG.keys():
            is_active = "active" if s_name == name else ""
            filename = PORTAL_CONFIG[s_name]["file"]
            series_links_html += f'<a href="{filename}" class="series-link {is_active}">{s_name}</a>\n'

        page_html = HTML_TEMPLATE.replace("{{SERIES_LINKS}}", series_links_html).format(
            series_name=name,
            series_slug=series_slug,
            primary_color=config["colors"]["primary"],
            primary_rgb=hex_to_rgb(config["colors"]["primary"]),
            accent_color=config["colors"]["accent"],
            accent_rgb=hex_to_rgb(config["colors"]["accent"]),
            bg_color=config["colors"]["bg"],
            hover_color=config["hover_color"],
            title_class=config["title_class"],
            bg_img=config["bg_img"],
            hero_desc=config["hero_desc"],
            nav_links=nav_links,
            chapters_html=chap_html,
            global_node_list=series_node_list,
            ga_id=GA_TRACKING_ID,
            footer_links=FOOTER_LINKS_HTML,
            favicon=config["favicon"],
            kinetic_header=KINETIC_HEADER_JS
        ).replace("{{SERIES_LINKS}}", series_links_html)
        
        # Preserve SEO content if it exists for portal pages
        injected_seo = "<!-- SEO_CONTENT_INJECTION_POINT -->"
        if os.path.exists(config["file"]):
            with open(config["file"], "r", encoding="utf-8") as f:
                content = f.read()
                if "<!-- SEO_CONTENT_INJECTED -->" in content:
                    start_marker = "<!-- SEO_CONTENT_INJECTED -->"
                    end_marker = "</section>"
                    start_idx = content.find(start_marker)
                    end_idx = content.find(end_marker, start_idx) + len(end_marker)
                    if start_idx != -1 and end_idx != -1:
                        injected_seo = content[start_idx:end_idx]

        page_html = page_html.replace("<!-- SEO_CONTENT_INJECTION_POINT -->", injected_seo)

        with open(config["file"], "w", encoding="utf-8") as f:
            f.write(page_html)
        
        print(f"Generating reader pages for {name}...")
        build_reader_pages(chapters, name, config["file"], CHAPTER_REGISTRY)
        
        print(f"Finalized {config['file']}")
    
    generate_sitemap()

def generate_sitemap():
    print("Generating sitemap.xml...")
    base_url = "https://bakidou.org"
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    
    # Homepage
    sitemap.append(f"  <url><loc>{base_url}/index.html</loc><priority>1.0</priority></url>")
    
    # Add portal pages
    for info in PORTAL_CONFIG.values():
        sitemap.append(f'  <url><loc>{base_url}/{info["file"]}</loc><priority>0.8</priority></url>')
    
    # Add footer pages
    footer_files = ["about.html", "contact.html", "privacy-policy.html", "dmca.html", "terms-of-service.html", "cookies-policy.html", "disclaimer.html"]
    for f in footer_files:
        sitemap.append(f'  <url><loc>{base_url}/{f}</loc><priority>0.4</priority></url>')

    # Add chapter pages
    for c in CHAPTER_REGISTRY:
        url = c['url'].replace('\\', '/')
        sitemap.append(f'  <url><loc>{base_url}/{url}</loc><priority>0.6</priority></url>')
    
    sitemap.append("</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap))
    print("sitemap.xml finalized.")

if __name__ == "__main__":
    build_sites()
