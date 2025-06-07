import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import base64
from io import StringIO
import zipfile
import tempfile
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Advanced Event Lobby Customizer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .preview-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .section-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class LobbyCustomizer:
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize session state with default configuration"""
        if 'config' not in st.session_state:
            st.session_state.config = {
                'layout': {
                    'section_order': ['live', 'upcoming', 'featured', 'finished', 'speakers'],
                    'section_visibility': {
                        'live': True, 'upcoming': True, 'featured': True, 
                        'finished': True, 'speakers': True
                    },
                    'grid_columns': 'repeat(auto-fit, minmax(400px, 1fr))',
                    'grid_gap': 25,
                    'section_spacing': 50,
                    'content_width': 1400,
                    'content_padding': 40,
                    'responsive_breakpoints': {
                        'mobile': 768,
                        'tablet': 1024,
                        'desktop': 1200
                    }
                },
                'header': {
                    'background_color': '#667eea',
                    'logo_text': 'TechConnect 2024',
                    'logo_color': '#ffffff',
                    'text_color': '#ffffff',
                    'logo_size': 28,
                    'padding': '15px 40px',
                    'show_live_indicator': True,
                    'show_bookmarks': True,
                    'show_user_info': True
                },
                'masthead': {
                    'background_type': 'gradient',
                    'background_gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'background_image': '',
                    'title_text': 'Welcome to TechConnect 2024',
                    'subtitle_text': 'The Future of Technology - Two Days of Innovation and Discovery',
                    'text_color': '#ffffff',
                    'title_size': 48,
                    'subtitle_size': 20,
                    'padding': '60px 40px',
                    'show_stats': True,
                    'show_countdown': False,
                    'custom_stats': [
                        {'number': '100+', 'label': 'Sessions'},
                        {'number': '150+', 'label': 'Speakers'},
                        {'number': '5000+', 'label': 'Attendees'}
                    ]
                },
                'navigation': {
                    'background_color': '#ffffff',
                    'text_color': '#6b7280',
                    'active_color': '#667eea',
                    'border_color': '#e5e7eb',
                    'tabs': ['Lobby', 'My Agenda', 'All Sessions', 'Speakers', 'Networking'],
                    'font_size': 16,
                    'height': 60
                },
                'session_card': {
                    'background_color': '#ffffff',
                    'border_radius': 12,
                    'shadow_color': 'rgba(0,0,0,0.08)',
                    'padding': 25,
                    'title_color': '#1f2937',
                    'text_color': '#4b5563',
                    'meta_color': '#6b7280',
                    'button_color': '#667eea',
                    'button_text_color': '#ffffff',
                    'border_width': 0,
                    'border_color': 'transparent',
                    'hover_effect': True,
                    'animation_duration': 0.3
                },
                'speaker_card': {
                    'background_color': '#ffffff',
                    'border_radius': 12,
                    'padding': 25,
                    'avatar_color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'name_color': '#1f2937',
                    'title_color': '#6b7280',
                    'shadow_color': 'rgba(0,0,0,0.08)',
                    'avatar_size': 80,
                    'show_session_count': True
                },
                'quick_actions': {
                    'background_color': '#ffffff',
                    'border_radius': 12,
                    'padding': 20,
                    'shadow_color': 'rgba(0,0,0,0.08)',
                    'search_placeholder': 'Search sessions, speakers, topics...',
                    'show_search': True,
                    'show_filters': True,
                    'show_actions': True,
                    'search_suggestions': True
                },
                'colors': {
                    'primary': '#667eea',
                    'secondary': '#764ba2',
                    'success': '#10b981',
                    'warning': '#fbbf24',
                    'error': '#ef4444',
                    'neutral': '#6b7280',
                    'body_background': '#f8fafc',
                    'text_primary': '#1f2937',
                    'text_secondary': '#6b7280'
                },
                'content': {
                    'sections': {
                        'live': {
                            'title': 'Live Now',
                            'subtitle': 'Join these sessions happening right now',
                            'icon': '🔴',
                            'enabled': True
                        },
                        'upcoming': {
                            'title': 'Coming Up Next',
                            'subtitle': 'Sessions starting in the next 2 hours',
                            'icon': '⏰',
                            'enabled': True
                        },
                        'featured': {
                            'title': 'Featured Sessions - Day 1',
                            'subtitle': 'Don\'t miss these highlighted sessions',
                            'icon': '⭐',
                            'enabled': True
                        },
                        'finished': {
                            'title': 'Finished Sessions',
                            'subtitle': 'Watch recordings of completed sessions',
                            'icon': '✅',
                            'enabled': True
                        },
                        'speakers': {
                            'title': 'Featured Speakers',
                            'subtitle': 'Meet our amazing lineup of industry experts',
                            'icon': '👥',
                            'enabled': True
                        }
                    },
                    'section_title_size': 28,
                    'section_title_color': '#1f2937',
                    'section_subtitle_color': '#6b7280'
                },
                'advanced': {
                    'custom_css': '',
                    'analytics_code': '',
                    'meta_tags': {
                        'description': 'Join TechConnect 2024 for cutting-edge technology sessions',
                        'keywords': 'technology, conference, AI, blockchain, quantum computing',
                        'author': 'TechConnect Organizers'
                    },
                    'social_sharing': {
                        'enabled': True,
                        'title': 'Join me at TechConnect 2024!',
                        'description': 'Discover the future of technology',
                        'image': ''
                    }
                }
            }
            
        if 'session_data' not in st.session_state:
            st.session_state.session_data = self.get_sample_session_data()
            
        if 'speaker_data' not in st.session_state:
            st.session_state.speaker_data = self.get_sample_speaker_data()

    def get_sample_session_data(self):
        """Generate sample session data"""
        return pd.DataFrame([
            {
                'id': 1,
                'title': 'Neural Networks & Deep Learning Frontiers',
                'speaker': 'Dr. Sarah Chen',
                'company': 'MIT AI Lab',
                'time': '10:00 AM - 11:00 AM',
                'description': 'Exploring cutting-edge neural architecture and their applications in autonomous systems.',
                'status': 'live',
                'featured': False,
                'track': 'AI/ML',
                'level': 'Advanced',
                'tags': ['AI', 'Neural Networks', 'Deep Learning']
            },
            {
                'id': 2,
                'title': 'Quantum Computing Breakthrough Applications',
                'speaker': 'Prof. Michael Zhang',
                'company': 'IBM Research',
                'time': '10:30 AM - 11:30 AM',
                'description': 'Real-world quantum computing applications in cryptography and optimization.',
                'status': 'live',
                'featured': False,
                'track': 'Quantum',
                'level': 'Expert',
                'tags': ['Quantum Computing', 'Cryptography', 'Optimization']
            },
            {
                'id': 3,
                'title': 'Blockchain Infrastructure & Scalability',
                'speaker': 'Elena Rodriguez',
                'company': 'Ethereum Foundation',
                'time': '10:15 AM - 11:15 AM',
                'description': 'Advanced blockchain architecture for enterprise-grade applications.',
                'status': 'live',
                'featured': False,
                'track': 'Blockchain',
                'level': 'Intermediate',
                'tags': ['Blockchain', 'Scalability', 'Infrastructure']
            },
            {
                'id': 4,
                'title': 'The Future of Autonomous Vehicles',
                'speaker': 'David Chen',
                'company': 'Tesla Autopilot',
                'time': '2:00 PM - 3:00 PM',
                'description': 'Next-generation self-driving technology and safety protocols.',
                'status': 'upcoming',
                'featured': True,
                'track': 'Automotive',
                'level': 'Intermediate',
                'tags': ['Autonomous Vehicles', 'AI', 'Safety']
            },
            {
                'id': 5,
                'title': 'DevOps & Cloud Infrastructure',
                'speaker': 'Tom Anderson',
                'company': 'Docker',
                'time': '8:00 AM - 9:00 AM',
                'description': 'Modern containerization strategies and deployment pipelines.',
                'status': 'finished',
                'featured': False,
                'track': 'DevOps',
                'level': 'Beginner',
                'tags': ['DevOps', 'Docker', 'Cloud']
            }
        ])

    def get_sample_speaker_data(self):
        """Generate sample speaker data"""
        return pd.DataFrame([
            {
                'name': 'Dr. Sarah Chen',
                'title': 'AI Research Director',
                'company': 'MIT AI Lab',
                'bio': 'Leading researcher in neural networks with 15+ years experience.',
                'sessions': 3,
                'twitter': '@sarahchen_ai',
                'linkedin': 'sarahchen',
                'photo': ''
            },
            {
                'name': 'Prof. Michael Zhang',
                'title': 'Quantum Researcher',
                'company': 'IBM Research',
                'bio': 'Pioneer in quantum computing applications and cryptography.',
                'sessions': 2,
                'twitter': '@mzhang_quantum',
                'linkedin': 'michaelzhang',
                'photo': ''
            },
            {
                'name': 'Elena Rodriguez',
                'title': 'Security Lead',
                'company': 'Ethereum Foundation',
                'bio': 'Blockchain security expert and distributed systems architect.',
                'sessions': 4,
                'twitter': '@elena_crypto',
                'linkedin': 'elenarodriguez',
                'photo': ''
            }
        ])

    def render_header(self):
        """Render the main header"""
        st.markdown("""
        <div class="main-header">
            <h1>🎨 Advanced Event Lobby Customizer</h1>
            <p>Create, customize, and deploy professional event lobbies with advanced features</p>
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar with all customization options"""
        with st.sidebar:
            st.title("🛠️ Customization Panel")
            
            # Quick Actions
            st.markdown("### 🚀 Quick Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Reset All", help="Reset to default configuration"):
                    self.reset_configuration()
                    st.success("Configuration reset!")
                    st.rerun()
                    
            with col2:
                if st.button("📋 Copy Config", help="Copy configuration to clipboard"):
                    st.code(json.dumps(st.session_state.config, indent=2))
            
            # Import/Export
            st.markdown("### 📥 Import/Export")
            
            # Configuration upload
            uploaded_config = st.file_uploader(
                "Upload Configuration", 
                type=['json'],
                help="Upload a previously exported configuration file"
            )
            if uploaded_config:
                try:
                    config_data = json.load(uploaded_config)
                    st.session_state.config = config_data
                    st.success("Configuration loaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading configuration: {e}")
            
            # Data upload
            uploaded_sessions = st.file_uploader(
                "Upload Session Data", 
                type=['csv', 'json'],
                help="Upload your event session data"
            )
            if uploaded_sessions:
                try:
                    if uploaded_sessions.name.endswith('.csv'):
                        session_data = pd.read_csv(uploaded_sessions)
                    else:
                        session_data = pd.read_json(uploaded_sessions)
                    st.session_state.session_data = session_data
                    st.success(f"Loaded {len(session_data)} sessions!")
                except Exception as e:
                    st.error(f"Error loading session data: {e}")
            
            # Export buttons
            if st.button("📥 Export Configuration"):
                self.export_configuration()
                
            if st.button("🌐 Export Complete Package"):
                self.export_complete_package()

    def render_tabs(self):
        """Render the main customization tabs"""
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "📐 Layout", "🎨 Header", "🏆 Masthead", "📋 Navigation", 
            "📄 Sessions", "👥 Speakers", "⚡ Actions", "🎨 Theme", "⚙️ Advanced"
        ])
        
        with tab1:
            self.render_layout_tab()
            
        with tab2:
            self.render_header_tab()
            
        with tab3:
            self.render_masthead_tab()
            
        with tab4:
            self.render_navigation_tab()
            
        with tab5:
            self.render_sessions_tab()
            
        with tab6:
            self.render_speakers_tab()
            
        with tab7:
            self.render_actions_tab()
            
        with tab8:
            self.render_theme_tab()
            
        with tab9:
            self.render_advanced_tab()

    def render_layout_tab(self):
        """Render layout customization options"""
        st.markdown("### 📐 Layout & Sections")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Section Order & Visibility")
            
            # Section reordering
            sections = st.session_state.config['content']['sections']
            section_order = st.session_state.config['layout']['section_order']
            
            new_order = []
            for section_id in section_order:
                if section_id in sections:
                    section_info = sections[section_id]
                    col_a, col_b = st.columns([4, 1])
                    
                    with col_a:
                        st.write(f"{section_info['icon']} {section_info['title']}")
                    
                    with col_b:
                        enabled = st.checkbox(
                            "Show", 
                            value=st.session_state.config['layout']['section_visibility'][section_id],
                            key=f"vis_{section_id}"
                        )
                        st.session_state.config['layout']['section_visibility'][section_id] = enabled
                    
                    new_order.append(section_id)
            
            # Manual reordering
            st.markdown("##### Reorder Sections")
            reordered = st.multiselect(
                "Drag to reorder sections",
                options=new_order,
                default=new_order,
                format_func=lambda x: f"{sections[x]['icon']} {sections[x]['title']}"
            )
            if reordered != new_order:
                st.session_state.config['layout']['section_order'] = reordered
        
        with col2:
            st.markdown("#### Grid & Spacing")
            
            st.session_state.config['layout']['grid_gap'] = st.slider(
                "Grid Gap (px)", 
                min_value=10, 
                max_value=50, 
                value=st.session_state.config['layout']['grid_gap'],
                key="layout_grid_gap"
            )
            
            st.session_state.config['layout']['section_spacing'] = st.slider(
                "Section Spacing (px)", 
                min_value=20, 
                max_value=100, 
                value=st.session_state.config['layout']['section_spacing'],
                key="layout_section_spacing"
            )
            
            st.session_state.config['layout']['content_width'] = st.slider(
                "Content Width (px)", 
                min_value=1000, 
                max_value=1600, 
                value=st.session_state.config['layout']['content_width'],
                key="layout_content_width"
            )
            
            st.session_state.config['layout']['content_padding'] = st.slider(
                "Content Padding (px)", 
                min_value=20, 
                max_value=80, 
                value=st.session_state.config['layout']['content_padding'],
                key="layout_content_padding"
            )
            
            # Advanced grid settings
            st.markdown("##### Advanced Grid")
            st.session_state.config['layout']['grid_columns'] = st.text_input(
                "Grid Columns (CSS)",
                value=st.session_state.config['layout']['grid_columns'],
                help="CSS grid-template-columns value"
            )

    def render_header_tab(self):
        """Render header customization options"""
        st.markdown("### 🎨 Header Customization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Design")
            st.session_state.config['header']['background_color'] = st.color_picker(
                "Background Color", 
                value=st.session_state.config['header']['background_color'],
                key="header_bg_color"
            )
            
            st.session_state.config['header']['text_color'] = st.color_picker(
                "Text Color", 
                value=st.session_state.config['header']['text_color'],
                key="header_text_color"
            )
            
            st.session_state.config['header']['logo_color'] = st.color_picker(
                "Logo Color", 
                value=st.session_state.config['header']['logo_color'],
                key="header_logo_color"
            )
            
            st.session_state.config['header']['logo_size'] = st.slider(
                "Logo Size (px)", 
                min_value=20, 
                max_value=48, 
                value=st.session_state.config['header']['logo_size'],
                key="header_logo_size"
            )
        
        with col2:
            st.markdown("#### Content")
            st.session_state.config['header']['logo_text'] = st.text_input(
                "Logo Text", 
                value=st.session_state.config['header']['logo_text']
            )
            
            st.session_state.config['header']['padding'] = st.text_input(
                "Padding", 
                value=st.session_state.config['header']['padding'],
                help="CSS padding value (e.g., '15px 40px')"
            )
            
            st.markdown("#### Features")
            st.session_state.config['header']['show_live_indicator'] = st.checkbox(
                "Show Live Indicator", 
                value=st.session_state.config['header']['show_live_indicator'],
                key="header_show_live_indicator"
            )
            
            st.session_state.config['header']['show_bookmarks'] = st.checkbox(
                "Show Bookmarks", 
                value=st.session_state.config['header']['show_bookmarks'],
                key="header_show_bookmarks"
            )
            
            st.session_state.config['header']['show_user_info'] = st.checkbox(
                "Show User Info", 
                value=st.session_state.config['header']['show_user_info'],
                key="header_show_user_info"
            )

    def render_masthead_tab(self):
        """Render masthead customization options"""
        st.markdown("### 🏆 Masthead (Hero Section)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Background")
            bg_type = st.selectbox(
                "Background Type",
                options=['gradient', 'image', 'color'],
                index=['gradient', 'image', 'color'].index(st.session_state.config['masthead']['background_type'])
            )
            st.session_state.config['masthead']['background_type'] = bg_type
            
            if bg_type == 'gradient':
                st.session_state.config['masthead']['background_gradient'] = st.text_input(
                    "CSS Gradient", 
                    value=st.session_state.config['masthead']['background_gradient'],
                    help="e.g., linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                )
            elif bg_type == 'image':
                st.session_state.config['masthead']['background_image'] = st.text_input(
                    "Image URL", 
                    value=st.session_state.config['masthead']['background_image']
                )
            
            st.session_state.config['masthead']['text_color'] = st.color_picker(
                "Text Color", 
                value=st.session_state.config['masthead']['text_color'],
                key="masthead_text_color"
            )
        
        with col2:
            st.markdown("#### Content")
            st.session_state.config['masthead']['title_text'] = st.text_input(
                "Title", 
                value=st.session_state.config['masthead']['title_text']
            )
            
            st.session_state.config['masthead']['subtitle_text'] = st.text_area(
                "Subtitle", 
                value=st.session_state.config['masthead']['subtitle_text'],
                height=100
            )
            
            st.session_state.config['masthead']['title_size'] = st.slider(
                "Title Size (px)", 
                min_value=24, 
                max_value=72, 
                value=st.session_state.config['masthead']['title_size'],
                key="masthead_title_size"
            )
            
            st.session_state.config['masthead']['subtitle_size'] = st.slider(
                "Subtitle Size (px)", 
                min_value=14, 
                max_value=32, 
                value=st.session_state.config['masthead']['subtitle_size'],
                key="masthead_subtitle_size"
            )
        
        # Event Statistics
        st.markdown("#### Event Statistics")
        st.session_state.config['masthead']['show_stats'] = st.checkbox(
            "Show Statistics", 
            value=st.session_state.config['masthead']['show_stats'],
            key="masthead_show_stats"
        )
        
        if st.session_state.config['masthead']['show_stats']:
            st.markdown("##### Customize Stats")
            stats = st.session_state.config['masthead']['custom_stats']
            
            for i, stat in enumerate(stats):
                col_a, col_b, col_c = st.columns([2, 2, 1])
                with col_a:
                    stats[i]['number'] = st.text_input(f"Number {i+1}", value=stat['number'], key=f"stat_num_{i}")
                with col_b:
                    stats[i]['label'] = st.text_input(f"Label {i+1}", value=stat['label'], key=f"stat_label_{i}")
                with col_c:
                    if st.button("🗑️", key=f"del_stat_{i}") and len(stats) > 1:
                        stats.pop(i)
                        st.rerun()
            
            if st.button("➕ Add Stat"):
                stats.append({'number': '0', 'label': 'New Stat'})
                st.rerun()

    def render_navigation_tab(self):
        """Render navigation customization options"""
        st.markdown("### 📋 Navigation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Design")
            st.session_state.config['navigation']['background_color'] = st.color_picker(
                "Background Color", 
                value=st.session_state.config['navigation']['background_color'],
                key="nav_bg_color"
            )
            
            st.session_state.config['navigation']['text_color'] = st.color_picker(
                "Text Color", 
                value=st.session_state.config['navigation']['text_color'],
                key="nav_text_color"
            )
            
            st.session_state.config['navigation']['active_color'] = st.color_picker(
                "Active Tab Color", 
                value=st.session_state.config['navigation']['active_color'],
                key="nav_active_color"
            )
            
            st.session_state.config['navigation']['border_color'] = st.color_picker(
                "Border Color", 
                value=st.session_state.config['navigation']['border_color'],
                key="nav_border_color"
            )
        
        with col2:
            st.markdown("#### Settings")
            st.session_state.config['navigation']['font_size'] = st.slider(
                "Font Size (px)", 
                min_value=12, 
                max_value=24, 
                value=st.session_state.config['navigation']['font_size'],
                key="nav_font_size"
            )
            
            st.session_state.config['navigation']['height'] = st.slider(
                "Height (px)", 
                min_value=40, 
                max_value=100, 
                value=st.session_state.config['navigation']['height'],
                key="nav_height"
            )
        
        # Navigation Tabs Management
        st.markdown("#### Navigation Tabs")
        tabs = st.session_state.config['navigation']['tabs']
        
        for i, tab in enumerate(tabs):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                tabs[i] = st.text_input(f"Tab {i+1}", value=tab, key=f"nav_tab_{i}")
            with col_b:
                if st.button("🗑️", key=f"del_nav_{i}") and len(tabs) > 1:
                    tabs.pop(i)
                    st.rerun()
        
        if st.button("➕ Add Navigation Tab"):
            tabs.append("New Tab")
            st.rerun()

    def render_sessions_tab(self):
        """Render session customization options"""
        st.markdown("### 📄 Session Cards")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Card Design")
            st.session_state.config['session_card']['background_color'] = st.color_picker(
                "Background Color", 
                value=st.session_state.config['session_card']['background_color'],
                key="session_bg_color"
            )
            
            st.session_state.config['session_card']['border_radius'] = st.slider(
                "Border Radius (px)", 
                min_value=0, 
                max_value=24, 
                value=st.session_state.config['session_card']['border_radius'],
                key="session_border_radius"
            )
            
            st.session_state.config['session_card']['padding'] = st.slider(
                "Padding (px)", 
                min_value=15, 
                max_value=40, 
                value=st.session_state.config['session_card']['padding'],
                key="session_padding"
            )
            
            st.session_state.config['session_card']['shadow_color'] = st.text_input(
                "Shadow Color", 
                value=st.session_state.config['session_card']['shadow_color'],
                help="e.g., rgba(0,0,0,0.08)"
            )
        
        with col2:
            st.markdown("#### Colors")
            st.session_state.config['session_card']['title_color'] = st.color_picker(
                "Title Color", 
                value=st.session_state.config['session_card']['title_color'],
                key="session_title_color"
            )
            
            st.session_state.config['session_card']['text_color'] = st.color_picker(
                "Text Color", 
                value=st.session_state.config['session_card']['text_color'],
                key="session_text_color"
            )
            
            st.session_state.config['session_card']['meta_color'] = st.color_picker(
                "Meta Text Color", 
                value=st.session_state.config['session_card']['meta_color'],
                key="session_meta_color"
            )
            
            st.session_state.config['session_card']['button_color'] = st.color_picker(
                "Button Color", 
                value=st.session_state.config['session_card']['button_color'],
                key="session_button_color"
            )
            
            st.session_state.config['session_card']['button_text_color'] = st.color_picker(
                "Button Text Color", 
                value=st.session_state.config['session_card']['button_text_color'],
                key="session_button_text_color"
            )
        
        # Effects
        st.markdown("#### Effects")
        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.config['session_card']['hover_effect'] = st.checkbox(
                "Hover Effect", 
                value=st.session_state.config['session_card']['hover_effect'],
                key="session_hover_effect"
            )
        with col_b:
            st.session_state.config['session_card']['animation_duration'] = st.slider(
                "Animation Duration (s)", 
                min_value=0.1, 
                max_value=1.0, 
                value=st.session_state.config['session_card']['animation_duration'],
                step=0.1,
                key="session_animation_duration"
            )
        
        # Session Data Management
        st.markdown("#### Session Data")
        if st.checkbox("Edit Session Data", key="edit_session_data_checkbox"):
            edited_df = st.data_editor(
                st.session_state.session_data,
                num_rows="dynamic",
                use_container_width=True
            )
            st.session_state.session_data = edited_df

    def render_speakers_tab(self):
        """Render speaker customization options"""
        st.markdown("### 👥 Speaker Cards")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Card Design")
            st.session_state.config['speaker_card']['background_color'] = st.color_picker(
                "Background Color", 
                value=st.session_state.config['speaker_card']['background_color'],
                key="speaker_bg_color"
            )
            
            st.session_state.config['speaker_card']['border_radius'] = st.slider(
                "Border Radius (px)", 
                min_value=0, 
                max_value=24, 
                value=st.session_state.config['speaker_card']['border_radius'],
                key="speaker_border_radius"
            )
            
            st.session_state.config['speaker_card']['padding'] = st.slider(
                "Padding (px)", 
                min_value=15, 
                max_value=40, 
                value=st.session_state.config['speaker_card']['padding'],
                key="speaker_padding"
            )
            
            st.session_state.config['speaker_card']['avatar_size'] = st.slider(
                "Avatar Size (px)", 
                min_value=60, 
                max_value=120, 
                value=st.session_state.config['speaker_card']['avatar_size'],
                key="speaker_avatar_size"
            )
        
        with col2:
            st.markdown("#### Colors")
            st.session_state.config['speaker_card']['name_color'] = st.color_picker(
                "Name Color", 
                value=st.session_state.config['speaker_card']['name_color'],
                key="speaker_name_color"
            )
            
            st.session_state.config['speaker_card']['title_color'] = st.color_picker(
                "Title Color", 
                value=st.session_state.config['speaker_card']['title_color'],
                key="speaker_title_color"
            )
            
            st.session_state.config['speaker_card']['avatar_color'] = st.text_input(
                "Avatar Background", 
                value=st.session_state.config['speaker_card']['avatar_color'],
                help="CSS gradient or color"
            )
            
            st.session_state.config['speaker_card']['show_session_count'] = st.checkbox(
                "Show Session Count", 
                value=st.session_state.config['speaker_card']['show_session_count'],
                key="speaker_show_session_count"
            )
        
        # Speaker Data Management
        st.markdown("#### Speaker Data")
        if st.checkbox("Edit Speaker Data", key="edit_speaker_data_checkbox"):
            edited_df = st.data_editor(
                st.session_state.speaker_data,
                num_rows="dynamic",
                use_container_width=True
            )
            st.session_state.speaker_data = edited_df

    def render_actions_tab(self):
        """Render quick actions customization"""
        st.markdown("### ⚡ Quick Actions Bar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Design")
            st.session_state.config['quick_actions']['background_color'] = st.color_picker(
                "Background Color", 
                value=st.session_state.config['quick_actions']['background_color'],
                key="actions_bg_color"
            )
            
            st.session_state.config['quick_actions']['border_radius'] = st.slider(
                "Border Radius (px)", 
                min_value=0, 
                max_value=24, 
                value=st.session_state.config['quick_actions']['border_radius'],
                key="actions_border_radius"
            )
            
            st.session_state.config['quick_actions']['padding'] = st.slider(
                "Padding (px)", 
                min_value=10, 
                max_value=40, 
                value=st.session_state.config['quick_actions']['padding'],
                key="actions_padding"
            )
        
        with col2:
            st.markdown("#### Features")
            st.session_state.config['quick_actions']['show_search'] = st.checkbox(
                "Show Search Bar", 
                value=st.session_state.config['quick_actions']['show_search'],
                key="actions_show_search"
            )
            
            st.session_state.config['quick_actions']['show_filters'] = st.checkbox(
                "Show Filter Buttons", 
                value=st.session_state.config['quick_actions']['show_filters'],
                key="actions_show_filters"
            )
            
            st.session_state.config['quick_actions']['show_actions'] = st.checkbox(
                "Show Action Buttons", 
                value=st.session_state.config['quick_actions']['show_actions'],
                key="actions_show_actions"
            )
            
            st.session_state.config['quick_actions']['search_suggestions'] = st.checkbox(
                "Search Suggestions", 
                value=st.session_state.config['quick_actions']['search_suggestions'],
                key="actions_search_suggestions"
            )
        
        # Search Configuration
        if st.session_state.config['quick_actions']['show_search']:
            st.session_state.config['quick_actions']['search_placeholder'] = st.text_input(
                "Search Placeholder", 
                value=st.session_state.config['quick_actions']['search_placeholder']
            )

    def render_theme_tab(self):
        """Render theme and global color settings"""
        st.markdown("### 🎨 Theme & Colors")
        
        # Predefined themes
        st.markdown("#### Preset Themes")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔵 Default Blue"):
                self.apply_theme('default')
                
        with col2:
            if st.button("🟢 Green Tech"):
                self.apply_theme('green')
                
        with col3:
            if st.button("🟣 Purple Pro"):
                self.apply_theme('purple')
                
        with col4:
            if st.button("🔴 Red Energy"):
                self.apply_theme('red')
        
        # Custom colors
        st.markdown("#### Custom Colors")
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.config['colors']['primary'] = st.color_picker(
                "Primary Color", 
                value=st.session_state.config['colors']['primary'],
                key="theme_primary_color"
            )
            
            st.session_state.config['colors']['secondary'] = st.color_picker(
                "Secondary Color", 
                value=st.session_state.config['colors']['secondary'],
                key="theme_secondary_color"
            )
            
            st.session_state.config['colors']['success'] = st.color_picker(
                "Success Color", 
                value=st.session_state.config['colors']['success'],
                key="theme_success_color"
            )
            
            st.session_state.config['colors']['warning'] = st.color_picker(
                "Warning Color", 
                value=st.session_state.config['colors']['warning'],
                key="theme_warning_color"
            )
        
        with col2:
            st.session_state.config['colors']['error'] = st.color_picker(
                "Error Color", 
                value=st.session_state.config['colors']['error'],
                key="theme_error_color"
            )
            
            st.session_state.config['colors']['neutral'] = st.color_picker(
                "Neutral Color", 
                value=st.session_state.config['colors']['neutral'],
                key="theme_neutral_color"
            )
            
            st.session_state.config['colors']['body_background'] = st.color_picker(
                "Body Background", 
                value=st.session_state.config['colors']['body_background'],
                key="theme_body_bg_color"
            )
            
            st.session_state.config['colors']['text_primary'] = st.color_picker(
                "Primary Text", 
                value=st.session_state.config['colors']['text_primary'],
                key="theme_text_primary_color"
            )

    def render_advanced_tab(self):
        """Render advanced settings"""
        st.markdown("### ⚙️ Advanced Settings")
        
        # Custom CSS
        st.markdown("#### Custom CSS")
        st.session_state.config['advanced']['custom_css'] = st.text_area(
            "Additional CSS", 
            value=st.session_state.config['advanced']['custom_css'],
            height=150,
            help="Add custom CSS to override or extend styling"
        )
        
        # Analytics
        st.markdown("#### Analytics")
        st.session_state.config['advanced']['analytics_code'] = st.text_area(
            "Analytics Code", 
            value=st.session_state.config['advanced']['analytics_code'],
            height=100,
            help="Google Analytics, Facebook Pixel, or other tracking code"
        )
        
        # Meta Tags
        st.markdown("#### SEO & Meta Tags")
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.config['advanced']['meta_tags']['description'] = st.text_area(
                "Meta Description", 
                value=st.session_state.config['advanced']['meta_tags']['description']
            )
            
            st.session_state.config['advanced']['meta_tags']['keywords'] = st.text_input(
                "Keywords", 
                value=st.session_state.config['advanced']['meta_tags']['keywords']
            )
        
        with col2:
            st.session_state.config['advanced']['meta_tags']['author'] = st.text_input(
                "Author", 
                value=st.session_state.config['advanced']['meta_tags']['author']
            )
        
        # Social Sharing
        st.markdown("#### Social Sharing")
        st.session_state.config['advanced']['social_sharing']['enabled'] = st.checkbox(
            "Enable Social Sharing", 
            value=st.session_state.config['advanced']['social_sharing']['enabled'],
            key="advanced_social_sharing_enabled"
        )
        
        if st.session_state.config['advanced']['social_sharing']['enabled']:
            st.session_state.config['advanced']['social_sharing']['title'] = st.text_input(
                "Share Title", 
                value=st.session_state.config['advanced']['social_sharing']['title']
            )
            
            st.session_state.config['advanced']['social_sharing']['description'] = st.text_area(
                "Share Description", 
                value=st.session_state.config['advanced']['social_sharing']['description']
            )

    def apply_theme(self, theme_name):
        """Apply a predefined theme"""
        themes = {
            'default': {
                'primary': '#667eea',
                'secondary': '#764ba2',
                'success': '#10b981',
                'warning': '#fbbf24',
                'error': '#ef4444'
            },
            'green': {
                'primary': '#10b981',
                'secondary': '#059669',
                'success': '#34d399',
                'warning': '#fbbf24',
                'error': '#ef4444'
            },
            'purple': {
                'primary': '#8b5cf6',
                'secondary': '#7c3aed',
                'success': '#10b981',
                'warning': '#fbbf24',
                'error': '#ef4444'
            },
            'red': {
                'primary': '#ef4444',
                'secondary': '#dc2626',
                'success': '#10b981',
                'warning': '#fbbf24',
                'error': '#f87171'
            }
        }
        
        if theme_name in themes:
            theme = themes[theme_name]
            for key, value in theme.items():
                st.session_state.config['colors'][key] = value
            st.success(f"Applied {theme_name.title()} theme!")
            st.rerun()

    def generate_css(self):
        """Generate CSS from configuration"""
        config = st.session_state.config
        
        css = f"""
/* Generated Event Lobby Styles */
:root {{
  --primary-color: {config['colors']['primary']};
  --secondary-color: {config['colors']['secondary']};
  --success-color: {config['colors']['success']};
  --warning-color: {config['colors']['warning']};
  --error-color: {config['colors']['error']};
  --neutral-color: {config['colors']['neutral']};
  --body-bg: {config['colors']['body_background']};
  --text-primary: {config['colors']['text_primary']};
  --text-secondary: {config['colors']['text_secondary']};
}}

/* Body */
body {{
  background: {config['colors']['body_background']} !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

/* Header */
.header {{
  background: {config['header']['background_color']} !important;
  color: {config['header']['text_color']} !important;
  padding: {config['header']['padding']} !important;
}}

.logo {{
  color: {config['header']['logo_color']} !important;
  font-size: {config['header']['logo_size']}px !important;
}}

/* Masthead */
.masthead {{
  background: {config['masthead']['background_gradient'] if config['masthead']['background_type'] == 'gradient' else config['masthead']['background_image']} !important;
  color: {config['masthead']['text_color']} !important;
  padding: {config['masthead']['padding']} !important;
}}

.masthead h1 {{
  font-size: {config['masthead']['title_size']}px !important;
}}

.masthead p {{
  font-size: {config['masthead']['subtitle_size']}px !important;
}}

/* Navigation */
.nav-tabs {{
  background: {config['navigation']['background_color']} !important;
  border-bottom-color: {config['navigation']['border_color']} !important;
  height: {config['navigation']['height']}px !important;
}}

.nav-tab {{
  color: {config['navigation']['text_color']} !important;
  font-size: {config['navigation']['font_size']}px !important;
}}

.nav-tab.active {{
  color: {config['navigation']['active_color']} !important;
  border-bottom-color: {config['navigation']['active_color']} !important;
}}

/* Content Layout */
.content {{
  max-width: {config['layout']['content_width']}px !important;
  padding: {config['layout']['content_padding']}px !important;
}}

.sessions-grid {{
  grid-template-columns: {config['layout']['grid_columns']} !important;
  gap: {config['layout']['grid_gap']}px !important;
}}

.section {{
  margin-bottom: {config['layout']['section_spacing']}px !important;
}}

.section-title {{
  font-size: {config['content']['section_title_size']}px !important;
  color: {config['content']['section_title_color']} !important;
}}

/* Session Cards */
.session-card {{
  background: {config['session_card']['background_color']} !important;
  border-radius: {config['session_card']['border_radius']}px !important;
  padding: {config['session_card']['padding']}px !important;
  box-shadow: 0 4px 20px {config['session_card']['shadow_color']} !important;
  transition: all {config['session_card']['animation_duration']}s ease !important;
}}

.session-title {{
  color: {config['session_card']['title_color']} !important;
}}

.session-description {{
  color: {config['session_card']['text_color']} !important;
}}

.session-time, .session-speakers {{
  color: {config['session_card']['meta_color']} !important;
}}

.btn-primary {{
  background: {config['session_card']['button_color']} !important;
  color: {config['session_card']['button_text_color']} !important;
}}

/* Speaker Cards */
.speaker-card {{
  background: {config['speaker_card']['background_color']} !important;
  border-radius: {config['speaker_card']['border_radius']}px !important;
  padding: {config['speaker_card']['padding']}px !important;
}}

.speaker-avatar {{
  background: {config['speaker_card']['avatar_color']} !important;
  width: {config['speaker_card']['avatar_size']}px !important;
  height: {config['speaker_card']['avatar_size']}px !important;
}}

.speaker-name {{
  color: {config['speaker_card']['name_color']} !important;
}}

.speaker-title {{
  color: {config['speaker_card']['title_color']} !important;
}}

/* Quick Actions */
.quick-actions {{
  background: {config['quick_actions']['background_color']} !important;
  border-radius: {config['quick_actions']['border_radius']}px !important;
  padding: {config['quick_actions']['padding']}px !important;
}}

/* Custom CSS */
{config['advanced']['custom_css']}
"""
        return css

    def generate_html(self):
        """Generate complete HTML file"""
        config = st.session_state.config
        css = self.generate_css()
        
        # Generate session cards HTML
        session_html = ""
        for _, session in st.session_state.session_data.iterrows():
            status_class = "live" if session['status'] == 'live' else "future" if session['status'] == 'upcoming' else "finished"
            status_text = "LIVE" if session['status'] == 'live' else "UPCOMING" if session['status'] == 'upcoming' else "ENDED"
            
            session_html += f"""
            <div class="session-card {'featured' if session.get('featured', False) else ''}">
                {'<div class="featured-badge">Featured</div>' if session.get('featured', False) else ''}
                <div class="session-status status-{status_class}">{status_text}</div>
                <div class="session-time">{session['time']}</div>
                <h3 class="session-title">{session['title']}</h3>
                <div class="session-speakers">👤 {session['speaker']}, {session['company']}</div>
                <div class="session-description">{session['description']}</div>
                <div class="session-actions">
                    <button class="btn-primary">
                        {'Join' if session['status'] == 'live' else 'Watch Recording' if session['status'] == 'finished' else 'View Details'}
                    </button>
                    <button class="bookmark-btn">🤍</button>
                </div>
            </div>
            """
        
        # Generate speaker cards HTML
        speaker_html = ""
        for _, speaker in st.session_state.speaker_data.iterrows():
            initial = speaker['name'][0].upper()
            speaker_html += f"""
            <div class="speaker-card">
                <div class="speaker-avatar">{initial}</div>
                <div class="speaker-name">{speaker['name']}</div>
                <div class="speaker-title">{speaker['title']}, {speaker['company']}</div>
                {'<div class="speaker-sessions">' + str(speaker["sessions"]) + ' sessions</div>' if config['speaker_card']['show_session_count'] else ''}
            </div>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['header']['logo_text']}</title>
    <meta name="description" content="{config['advanced']['meta_tags']['description']}">
    <meta name="keywords" content="{config['advanced']['meta_tags']['keywords']}">
    <meta name="author" content="{config['advanced']['meta_tags']['author']}">
    
    <!-- Social Sharing -->
    <meta property="og:title" content="{config['advanced']['social_sharing']['title']}">
    <meta property="og:description" content="{config['advanced']['social_sharing']['description']}">
    <meta property="og:type" content="website">
    
    <style>
        {css}
        
        /* Base styles from original lobby */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header-info {{
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 14px;
        }}
        
        .nav-tabs {{
            border-bottom: 1px solid var(--nav-border);
            display: flex;
            gap: 40px;
            padding: 0 40px;
        }}
        
        .nav-tab {{
            padding: 15px 0;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }}
        
        .nav-tab.active {{
            border-bottom-color: var(--nav-active);
        }}
        
        .masthead {{
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .masthead-content {{
            position: relative;
            z-index: 1;
        }}
        
        .event-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        .quick-actions {{
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 40px;
        }}
        
        .search-container {{
            position: relative;
            flex: 1;
            max-width: 400px;
        }}
        
        .search-input {{
            width: 100%;
            padding: 12px 20px 12px 45px;
            border: 2px solid #e5e7eb;
            border-radius: 25px;
            font-size: 14px;
            background: #f9fafb;
        }}
        
        .search-icon {{
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #9ca3af;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #e5e7eb;
            background: white;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            font-size: 14px;
        }}
        
        .filter-btn.active {{
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }}
        
        .sessions-grid {{
            display: grid;
            margin-bottom: 50px;
        }}
        
        .session-card {{
            border: 2px solid transparent;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .session-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}
        
        .session-card.featured {{
            background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 1%, white 1%);
        }}
        
        .featured-badge {{
            position: absolute;
            top: -2px;
            left: 15px;
            background: #fbbf24;
            color: white;
            padding: 4px 12px;
            border-radius: 0 0 8px 8px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .session-status {{
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-live {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .status-finished {{
            background: #f3f4f6;
            color: #6b7280;
        }}
        
        .status-future {{
            background: #dbeafe;
            color: #2563eb;
        }}
        
        .session-actions {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .btn-primary {{
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
        }}
        
        .bookmark-btn {{
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 8px;
            border-radius: 6px;
            transition: all 0.3s ease;
        }}
        
        .speakers-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
        }}
        
        .speaker-card {{
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }}
        
        .speaker-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}
        
        .speaker-avatar {{
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 32px;
            font-weight: bold;
        }}
        
        .speaker-name {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .speaker-title {{
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .speaker-sessions {{
            font-size: 12px;
            color: var(--primary-color);
            font-weight: 500;
        }}
        
        .section {{
            margin-bottom: var(--section-spacing, 50px);
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }}
        
        .section-title {{
            font-weight: bold;
        }}
        
        .section-subtitle {{
            font-size: 16px;
            margin-top: 5px;
        }}
        
        .view-all {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 8px;
            transition: background 0.3s ease;
        }}
        
        .view-all:hover {{
            background: #f3f4f6;
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 15px 20px;
                flex-direction: column;
                gap: 15px;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .sessions-grid {{
                grid-template-columns: 1fr;
            }}
            
            .quick-actions {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .masthead {{
                padding: 40px 20px;
            }}
            
            .event-stats {{
                flex-direction: column;
                gap: 20px;
            }}
        }}
    </style>
    
    {config['advanced']['analytics_code']}
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="logo">{config['header']['logo_text']}</div>
        <div class="header-info">
            {('<div>🔴 3 sessions live now</div>' if config['header']['show_live_indicator'] else '')}
            {('<div>📚 7 bookmarked</div>' if config['header']['show_bookmarks'] else '')}
            {('<div>Welcome, Alex Chen</div>' if config['header']['show_user_info'] else '')}
        </div>
    </div>

    <!-- Navigation -->
    <div class="nav-tabs">
        {(''.join([f'<div class="nav-tab {"active" if i == 0 else ""}">{tab}</div>' for i, tab in enumerate(config['navigation']['tabs'])]))}
    </div>

    <!-- Masthead -->
    <div class="masthead">
        <div class="masthead-content">
            <h1>{config['masthead']['title_text']}</h1>
            <p>{config['masthead']['subtitle_text']}</p>
            {(f"""
            <div class="event-stats">
                {(''.join([f'<div class="stat"><span class="stat-number">{stat["number"]}</span><span class="stat-label">{stat["label"]}</span></div>' for stat in config['masthead']['custom_stats']]))}
            </div>
            """ if config['masthead']['show_stats'] else '')}
        </div>
    </div>

    <!-- Content -->
    <div class="content">
        <!-- Quick Actions -->
        {(f"""
        <div class="quick-actions">
            {('<div class="search-container"><input type="text" class="search-input" placeholder="' + config['quick_actions']['search_placeholder'] + '"><span class="search-icon">🔍</span></div>' if config['quick_actions']['show_search'] else '')}
            {('<button class="filter-btn active">All Sessions</button><button class="filter-btn">Live Now</button><button class="filter-btn">Upcoming</button>' if config['quick_actions']['show_filters'] else '')}
            {('<button class="filter-btn">📅 Download Schedule</button>' if config['quick_actions']['show_actions'] else '')}
        </div>
        """ if any([config['quick_actions']['show_search'], config['quick_actions']['show_filters'], config['quick_actions']['show_actions']]) else '')}

        <!-- Sections -->
        {self.generate_sections_html(session_html, speaker_html)}
    </div>
</body>
</html>"""
        
        return html

    def generate_sections_html(self, session_html, speaker_html):
        """Generate HTML for all sections based on configuration"""
        config = st.session_state.config
        sections_html = ""
        
        for section_id in config['layout']['section_order']:
            if not config['layout']['section_visibility'][section_id]:
                continue
                
            section_info = config['content']['sections'][section_id]
            
            if section_id == 'speakers':
                sections_html += f"""
                <div class="section">
                    <div class="section-header">
                        <div>
                            <h2 class="section-title">{section_info['title']}</h2>
                            <p class="section-subtitle">{section_info['subtitle']}</p>
                        </div>
                        <a href="#" class="view-all">View all →</a>
                    </div>
                    <div class="speakers-grid">
                        {speaker_html}
                    </div>
                </div>
                """
            else:
                sections_html += f"""
                <div class="section">
                    <div class="section-header">
                        <div>
                            <h2 class="section-title">{section_info['title']}</h2>
                            <p class="section-subtitle">{section_info['subtitle']}</p>
                        </div>
                        <a href="#" class="view-all">View all →</a>
                    </div>
                    <div class="sessions-grid">
                        {session_html}
                    </div>
                </div>
                """
        
        return sections_html

    def render_preview(self):
        """Render live preview of the lobby"""
        st.markdown("### 🔍 Live Preview")
        
        with st.container():
            # Header Preview
            header_style = f"""
            background: {st.session_state.config['header']['background_color']};
            color: {st.session_state.config['header']['text_color']};
            padding: {st.session_state.config['header']['padding']};
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            """
            
            st.markdown(f"""
            <div style="{header_style}">
                <div style="font-size: {st.session_state.config['header']['logo_size']}px; font-weight: bold; color: {st.session_state.config['header']['logo_color']};">
                    {st.session_state.config['header']['logo_text']}
                </div>
                <div style="display: flex; gap: 20px; font-size: 14px;">
                    {('🔴 3 sessions live now' if st.session_state.config['header']['show_live_indicator'] else '')}
                    {('📚 7 bookmarked' if st.session_state.config['header']['show_bookmarks'] else '')}
                    {('Welcome, Alex Chen' if st.session_state.config['header']['show_user_info'] else '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Masthead Preview
            masthead_bg = (st.session_state.config['masthead']['background_gradient'] 
                          if st.session_state.config['masthead']['background_type'] == 'gradient' 
                          else st.session_state.config['masthead']['background_image'])
            
            masthead_style = f"""
            background: {masthead_bg};
            color: {st.session_state.config['masthead']['text_color']};
            padding: {st.session_state.config['masthead']['padding']};
            text-align: center;
            border-radius: 8px;
            margin-bottom: 20px;
            """
            
            st.markdown(f"""
            <div style="{masthead_style}">
                <h1 style="font-size: {st.session_state.config['masthead']['title_size']}px; margin-bottom: 15px;">
                    {st.session_state.config['masthead']['title_text']}
                </h1>
                <p style="font-size: {st.session_state.config['masthead']['subtitle_size']}px; opacity: 0.9;">
                    {st.session_state.config['masthead']['subtitle_text']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sample Session Cards
            st.markdown("#### Sample Session Cards")
            col1, col2 = st.columns(2)
            
            with col1:
                card_style = f"""
                background: {st.session_state.config['session_card']['background_color']};
                border-radius: {st.session_state.config['session_card']['border_radius']}px;
                padding: {st.session_state.config['session_card']['padding']}px;
                box-shadow: 0 4px 20px {st.session_state.config['session_card']['shadow_color']};
                margin-bottom: 20px;
                """
                
                st.markdown(f"""
                <div style="{card_style}">
                    <div style="color: {st.session_state.config['session_card']['meta_color']}; font-size: 14px; margin-bottom: 10px;">
                        10:00 AM - 11:00 AM
                    </div>
                    <h3 style="color: {st.session_state.config['session_card']['title_color']}; font-size: 20px; margin-bottom: 12px;">
                        Neural Networks & Deep Learning
                    </h3>
                    <div style="color: {st.session_state.config['session_card']['meta_color']}; font-size: 14px; margin-bottom: 15px;">
                        👤 Dr. Sarah Chen, MIT AI Lab
                    </div>
                    <div style="color: {st.session_state.config['session_card']['text_color']}; font-size: 14px; margin-bottom: 20px;">
                        Exploring cutting-edge neural architecture...
                    </div>
                    <button style="background: {st.session_state.config['session_card']['button_color']}; color: {st.session_state.config['session_card']['button_text_color']}; border: none; padding: 12px 24px; border-radius: 8px; width: 100%;">
                        Join Session
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Sample Speaker Card
                st.markdown("#### Sample Speaker Card")
                speaker_style = f"""
                background: {st.session_state.config['speaker_card']['background_color']};
                border-radius: {st.session_state.config['speaker_card']['border_radius']}px;
                padding: {st.session_state.config['speaker_card']['padding']}px;
                text-align: center;
                box-shadow: 0 4px 20px {st.session_state.config['speaker_card']['shadow_color']};
                """
                
                st.markdown(f"""
                <div style="{speaker_style}">
                    <div style="width: {st.session_state.config['speaker_card']['avatar_size']}px; height: {st.session_state.config['speaker_card']['avatar_size']}px; border-radius: 50%; background: {st.session_state.config['speaker_card']['avatar_color']}; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; color: white; font-size: 32px; font-weight: bold;">
                        S
                    </div>
                    <div style="color: {st.session_state.config['speaker_card']['name_color']}; font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                        Dr. Sarah Chen
                    </div>
                    <div style="color: {st.session_state.config['speaker_card']['title_color']}; font-size: 14px;">
                        AI Research Director, MIT
                    </div>
                </div>
                """, unsafe_allow_html=True)

    def export_configuration(self):
        """Export configuration as JSON"""
        config_json = json.dumps(st.session_state.config, indent=2)
        st.download_button(
            label="📥 Download Configuration",
            data=config_json,
            file_name=f"lobby_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    def export_complete_package(self):
        """Export complete package with HTML, CSS, and assets"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate files
            html_content = self.generate_html()
            css_content = self.generate_css()
            config_content = json.dumps(st.session_state.config, indent=2)
            
            # Write files
            with open(os.path.join(temp_dir, "index.html"), "w") as f:
                f.write(html_content)
            
            with open(os.path.join(temp_dir, "styles.css"), "w") as f:
                f.write(css_content)
                
            with open(os.path.join(temp_dir, "config.json"), "w") as f:
                f.write(config_content)
                
            # Export session data
            st.session_state.session_data.to_csv(os.path.join(temp_dir, "sessions.csv"), index=False)
            st.session_state.speaker_data.to_csv(os.path.join(temp_dir, "speakers.csv"), index=False)
            
            # Create README
            readme_content = f"""# {st.session_state.config['header']['logo_text']} - Event Lobby

## Files Included:
- `index.html` - Complete lobby HTML file
- `styles.css` - Generated CSS styles
- `config.json` - Configuration backup
- `sessions.csv` - Session data
- `speakers.csv` - Speaker data
- `README.md` - This file

## Usage:
1. Open `index.html` in a web browser to view your lobby
2. Upload to your web hosting service
3. Import `config.json` to restore settings in the customizer

## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(os.path.join(temp_dir, "README.md"), "w") as f:
                f.write(readme_content)
            
            # Create ZIP file
            zip_buffer = StringIO()
            with zipfile.ZipFile(f"{temp_dir}/lobby_package.zip", "w") as zip_file:
                for file_name in ["index.html", "styles.css", "config.json", "sessions.csv", "speakers.csv", "README.md"]:
                    zip_file.write(os.path.join(temp_dir, file_name), file_name)
            
            # Offer download
            with open(f"{temp_dir}/lobby_package.zip", "rb") as f:
                zip_data = f.read()
                
            st.download_button(
                label="📦 Download Complete Package",
                data=zip_data,
                file_name=f"lobby_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )

    def reset_configuration(self):
        """Reset configuration to defaults"""
        for key in list(st.session_state.keys()):
            if key.startswith('config') or key.startswith('session_data') or key.startswith('speaker_data'):
                del st.session_state[key]
        self.initialize_session_state()

    def run(self):
        """Main application runner"""
        self.render_header()
        
        # Create main layout
        self.render_sidebar()
        
        # Main content area
        self.render_tabs()
        
        # Preview section
        with st.expander("🔍 Live Preview", expanded=True):
            self.render_preview()

# Run the application
if __name__ == "__main__":
    app = LobbyCustomizer()
    app.run()
