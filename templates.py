import random
from config import *

def get_base_template(title, content, include_particles=True):
    particles_html = ''
    if include_particles:
        dots = []
        for _ in range(18):
            dots.append('<div class="particle" style="left: ' + str(random.randint(0, 100)) + '%; animation-delay: ' + str(random.randint(0, 20)) + 's;"></div>')
        glyphs_chars = ['ア','ニ','メ','力','神','炎','風','光','ナ','カ','ラ','サ','タ','ハ','ひ','ネ']
        glyphs = []
        for _ in range(14):
            g = random.choice(glyphs_chars)
            glyphs.append('<div class="glyph" style="left:' + str(random.randint(0, 100)) + '%; animation-delay:' + str(random.randint(0, 18)) + 's;">' + g + '</div>')
        particles_html = '<div class="floating-particles">' + ''.join(dots + glyphs) + '</div>'
    
    # Firebase SDK (for auth only)
    firebase_sdk = '''
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-auth-compat.js"></script>
    <script>
        const firebaseConfig = {
            apiKey: "''' + FIREBASE_CONFIG["apiKey"] + '''",
            authDomain: "''' + FIREBASE_CONFIG["authDomain"] + '''",
            projectId: "''' + FIREBASE_CONFIG["projectId"] + '''",
            storageBucket: "''' + FIREBASE_CONFIG["storageBucket"] + '''",
            messagingSenderId: "''' + FIREBASE_CONFIG["messagingSenderId"] + '''",
            appId: "''' + FIREBASE_CONFIG["appId"] + '''"
        };
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
    </script>
    '''
    
    return (
    '<!DOCTYPE html><html lang="en"><head>'
    '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
    '<title>' + str(title) + '</title>'
    '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">'
    + str(COMPLETE_STYLE) +
    '</head><body>'
    '<div class="animated-bg"><div class="grid-animation"></div>' + str(particles_html) + '</div>'
    '<div class="container">' + str(content) + '</div>'
    '<div id="toast" class="toast"></div>'
    '<div id="soundIndicator" class="sound-indicator" onclick="toggleSound()" title="Toggle Sound"><i class="fas fa-volume-up"></i></div>'
    + str(firebase_sdk)
    + str(GLOBAL_SCRIPT) +
    '</body></html>'
)

# Complete Enhanced Style with Advanced Animations and Mobile Fixes
COMPLETE_STYLE = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    
    :root {
        --primary-black: #050505; 
        --secondary-black: #0d0d0f; 
        --tertiary-black: #18181b;
        --primary-red: #dc2626; 
        --secondary-red: #991b1b; 
        --accent-red: #ff4444; 
        --neon-red: #ff0040;
        --text-light: #ffffff; 
        --text-gray: #9ca3af; 
        --text-dark-gray: #6b7280; 
        --border-color: #2a2a2a;
        --success-green: #22c55e; 
        --warning-yellow: #eab308; 
        --info-blue: #3b82f6;
        --purple-accent: #a855f7; 
        --pink-accent: #ec4899;
    }
    
    body { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
        background: #000; 
        min-height: 100vh; 
        color: var(--text-light); 
        position: relative; 
        overflow-x: hidden; 
    }
    
    /* Advanced Animated Background */
    .animated-bg { 
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%; 
        z-index: 0; 
        background: radial-gradient(1200px 600px at 80% -10%, rgba(167, 139, 250, 0.15), transparent 60%), 
                    radial-gradient(900px 500px at -10% 110%, rgba(239, 68, 68, 0.15), transparent 60%), 
                    linear-gradient(135deg, #050505 0%, #0d0d0f 100%); 
    }
    
    .animated-bg::before {
        content: ''; 
        position: absolute; 
        inset: 0;
        background-image: radial-gradient(circle at 20% 80%, rgba(220,38,38,0.1) 0%, transparent 50%), 
                         radial-gradient(circle at 80% 20%, rgba(168,85,247,0.08) 0%, transparent 50%), 
                         radial-gradient(circle at 40% 40%, rgba(236,72,153,0.06) 0%, transparent 50%);
        animation: gradientShift 16s ease-in-out infinite;
    }
    
    @keyframes gradientShift { 
        0%, 100% { transform: translate(0,0) rotate(0) }
        33% { transform: translate(-20px,-20px) rotate(120deg) }
        66% { transform: translate(20px,-20px) rotate(240deg) }
    }
    
    /* Grid Animation */
    .grid-animation { 
        position: absolute; 
        inset: 0; 
        background-image: linear-gradient(rgba(220,38,38,0.03) 1px, transparent 1px), 
                         linear-gradient(90deg, rgba(220,38,38,0.03) 1px, transparent 1px); 
        background-size: 50px 50px; 
        animation: gridMove 20s linear infinite; 
    }
    
    @keyframes gridMove { 
        0% { transform: translate(0,0) }
        100% { transform: translate(50px,50px) }
    }
    
    /* Particle Effects */
    .floating-particles { 
        position: absolute; 
        inset: 0; 
        overflow: hidden; 
        pointer-events: none; 
    }
    
    .particle { 
        position: absolute; 
        width: 4px; 
        height: 4px; 
        background: rgba(220,38,38,0.5); 
        border-radius: 50%; 
        animation: float 20s infinite; 
    }
    
    .particle:nth-child(odd) { 
        width: 2px; 
        height: 2px; 
        animation-duration: 26s; 
        background: rgba(168,85,247,0.5); 
    }
    
    .glyph { 
        position: absolute; 
        color: rgba(255,255,255,0.09); 
        font-size: 18px; 
        user-select: none; 
        animation: float 24s infinite; 
        text-shadow: 0 0 8px rgba(255,255,255,0.1), 0 0 20px rgba(236,72,153,0.15); 
    }
    
    @keyframes float { 
        0% { transform: translateY(100vh) translateX(0) scale(0.7); opacity: 0; }
        10% { opacity: .9; transform: scale(1); }
        90% { opacity: .9; }
        100% { transform: translateY(-100vh) translateX(120px) scale(0.7); opacity: 0; }
    }
    
    /* Layout */
    .container { 
        max-width: 1400px; 
        margin: 0 auto; 
        padding: 20px; 
        position: relative; 
        z-index: 2; 
    }
    
    /* Header Styles */
    .header { 
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); 
        padding: 40px; 
        border-radius: 25px; 
        margin-bottom: 40px; 
        border: 1px solid rgba(220,38,38,0.2); 
        backdrop-filter: blur(20px);
        animation: slideDown 0.6s ease;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .header h1 { 
        font-size: 3.2rem; 
        font-weight: 900; 
        background: linear-gradient(135deg, var(--primary-red), var(--accent-red), var(--purple-accent)); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        margin-bottom: 10px; 
        text-transform: uppercase; 
        letter-spacing: 3px;
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    /* Credits Display */
    .credits-display { 
        position: fixed; 
        top: 20px; 
        left: 20px; 
        background: linear-gradient(135deg, rgba(34,197,94,0.25), rgba(34,197,94,0.1)); 
        padding: 12px 24px; 
        border-radius: 15px; 
        border: 1px solid rgba(34,197,94,0.3); 
        backdrop-filter: blur(20px); 
        z-index: 1000; 
        animation: pulse 2s ease infinite;
        transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 120px;
    }
    
    .credits-display:hover {
        transform: scale(1.05);
    }
    
    @keyframes pulse { 
        0%, 100% { transform: scale(1) }
        50% { transform: scale(1.02) }
    }
    
    /* User Info Bar */
    .user-info { 
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); 
        padding: 12px 24px; 
        border-radius: 15px; 
        border: 1px solid rgba(220,38,38,0.2); 
        backdrop-filter: blur(20px); 
        z-index: 1000; 
        display: flex; 
        align-items: center; 
        gap: 15px; 
        flex-wrap: wrap;
        animation: slideLeft 0.6s ease;
        max-width: calc(100% - 160px);
    }
    
    @keyframes slideLeft {
        from { transform: translateX(50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Tools Grid */
    .tools-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
        gap: 30px; 
        margin-top: 40px; 
    }
    
    .tool-card { 
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); 
        padding: 35px; 
        border-radius: 20px; 
        border: 1px solid rgba(220,38,38,0.1); 
        transition: all .4s cubic-bezier(.4,0,.2,1); 
        cursor: pointer; 
        position: relative; 
        overflow: hidden; 
        text-decoration: none; 
        display: block;
        animation: fadeUp 0.6s ease forwards;
        opacity: 0;
    }
    
    .tool-card:nth-child(1) { animation-delay: 0.1s; }
    .tool-card:nth-child(2) { animation-delay: 0.2s; }
    .tool-card:nth-child(3) { animation-delay: 0.3s; }
    .tool-card:nth-child(4) { animation-delay: 0.4s; }
    .tool-card:nth-child(5) { animation-delay: 0.5s; }
    .tool-card:nth-child(6) { animation-delay: 0.6s; }
    
    @keyframes fadeUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .tool-card::before { 
        content: ''; 
        position: absolute; 
        inset: 0; 
        background: linear-gradient(135deg, rgba(220,38,38,0.1), transparent); 
        opacity: 0; 
        transition: opacity .3s ease; 
    }
    
    .tool-card:hover::before { opacity: 1; }
    
    .tool-card:hover { 
        transform: translateY(-8px) scale(1.02); 
        box-shadow: 0 20px 40px rgba(220,38,38,0.3); 
        border-color: rgba(220,38,38,0.4); 
    }
    
    /* Search Container */
    .search-container { 
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); 
        padding: 50px; 
        border-radius: 25px; 
        border: 1px solid rgba(220,38,38,0.2); 
        margin-bottom: 40px; 
        backdrop-filter: blur(20px);
        animation: slideUp 0.6s ease;
    }
    
    @keyframes slideUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .search-form { 
        display: flex; 
        gap: 15px; 
        max-width: 700px; 
        margin: 0 auto; 
    }
    
    .search-input { 
        flex: 1; 
        padding: 18px 24px; 
        background: rgba(10,10,10,0.8); 
        border: 1px solid rgba(220,38,38,0.2); 
        border-radius: 15px; 
        color: var(--text-light); 
        font-size: 1.05rem; 
        transition: all .3s cubic-bezier(.4,0,.2,1); 
    }
    
    .search-input:focus {
        outline: none;
        border-color: var(--primary-red);
        box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
    }
    
    .search-btn { 
        padding: 18px 36px; 
        background: linear-gradient(135deg, var(--primary-red), var(--secondary-red)); 
        color: #fff; 
        border: none; 
        border-radius: 15px; 
        font-size: 1.05rem; 
        font-weight: 600; 
        cursor: pointer; 
        transition: all .3s cubic-bezier(.4,0,.2,1); 
        text-transform: uppercase; 
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
        white-space: nowrap;
    }
    
    .search-btn::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .search-btn:active::after {
        width: 300px;
        height: 300px;
    }
    
    .search-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(220,38,38,0.4);
    }
    
    /* Results Container */
    .results-container { 
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); 
        padding: 50px; 
        border-radius: 25px; 
        border: 1px solid rgba(220,38,38,0.2); 
        backdrop-filter: blur(20px);
        animation: fadeIn 0.6s ease;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .result-item { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 20px 25px; 
        background: linear-gradient(135deg, rgba(10,10,10,0.9), rgba(10,10,10,0.7)); 
        border-radius: 15px; 
        margin-bottom: 15px; 
        border: 1px solid rgba(220,38,38,0.1); 
        transition: all .3s cubic-bezier(.4,0,.2,1);
        animation: slideRight 0.4s ease;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    @keyframes slideRight {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .result-item:hover {
        transform: translateX(5px);
        border-color: rgba(220,38,38,0.3);
        box-shadow: 0 5px 15px rgba(220,38,38,0.2);
    }
    
    /* Loading Animation */
    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid rgba(220,38,38,0.1);
        border-top-color: var(--primary-red);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading p {
        margin-top: 20px;
        color: var(--text-gray);
        animation: blink 1.5s ease infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Forms */
    .form-group { 
        margin-bottom: 20px; 
    }
    
    .form-group label { 
        display: block; 
        margin-bottom: 8px; 
        color: var(--text-gray); 
        font-size: .9rem; 
        font-weight: 500; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
    }
    
    .form-group input, 
    .form-group select, 
    .form-group textarea { 
        width: 100%; 
        padding: 14px 18px; 
        background: rgba(10,10,10,0.8); 
        border: 1px solid rgba(220,38,38,0.2); 
        border-radius: 12px; 
        color: var(--text-light); 
        font-size: 1rem; 
        transition: all .3s cubic-bezier(.4,0,.2,1); 
        box-sizing: border-box;
    }
    
    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
        outline: none;
        border-color: var(--primary-red);
        box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
    }
    
    /* Buttons */
    .btn { 
        padding: 14px 30px; 
        background: linear-gradient(135deg, var(--primary-red), var(--secondary-red)); 
        color: #fff; 
        border: none; 
        border-radius: 12px; 
        font-size: 1rem; 
        font-weight: 600; 
        cursor: pointer; 
        transition: all .3s cubic-bezier(.4,0,.2,1); 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        position: relative; 
        overflow: hidden; 
        white-space: nowrap;
        text-align: center;
        display: inline-block;
    }
    
    .btn:hover { 
        transform: translateY(-3px) scale(1.02); 
        box-shadow: 0 10px 30px rgba(220,38,38,0.5); 
    }
    
    .btn-alt { 
        background: linear-gradient(135deg, #374151, #1f2937); 
    }
    
    .btn-danger {
        background: linear-gradient(135deg, var(--primary-red), var(--secondary-red));
    }
    
    /* Copy Button */
    .copy-btn {
        padding: 6px 12px;
        font-size: .8rem;
        background: linear-gradient(135deg, var(--primary-red), var(--secondary-red));
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-left: 10px;
        white-space: nowrap;
    }
    
    .copy-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(220,38,38,0.4);
    }
    
    .copy-btn:active {
        transform: scale(0.95);
    }
    
    .copy-btn.copied {
        background: linear-gradient(135deg, var(--success-green), #16a34a);
    }
    
    /* Data Display */
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .data-card {
        background: rgba(10,10,10,0.5);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(220,38,38,0.1);
        transition: all 0.3s ease;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .data-card:hover {
        transform: translateY(-2px);
        border-color: rgba(220,38,38,0.3);
    }
    
    .data-label {
        color: var(--text-gray);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .data-value {
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    /* Status Badges */
    .status-badge { 
        padding: 4px 10px; 
        border-radius: 12px; 
        font-size: .8rem; 
        font-weight: 600; 
        text-transform: uppercase; 
        white-space: nowrap;
    }
    
    .status-active { 
        background: rgba(34,197,94,0.2); 
        color: var(--success-green); 
        border: 1px solid rgba(34,197,94,0.3); 
    }
    
    .status-online { 
        background: rgba(34,197,94,0.2); 
        color: var(--success-green); 
        border: 1px solid rgba(34,197,94,0.3); 
    }
    
    .status-offline { 
        background: rgba(107,114,128,0.2); 
        color: var(--text-gray); 
        border: 1px solid rgba(107,114,128,0.3); 
    }
    
    /* Ticket Card */
    .ticket-card { 
        background: linear-gradient(135deg, rgba(10,10,10,0.9), rgba(10,10,10,0.7)); 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid rgba(220,38,38,0.1); 
        transition: all .3s ease; 
        cursor: pointer; 
        margin-bottom: 20px; 
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .ticket-card:hover {
        transform: translateX(5px);
        border-color: rgba(220,38,38,0.3);
        box-shadow: 0 5px 15px rgba(220,38,38,0.2);
    }
    
    /* File Upload */
    .file-upload {
        position: relative;
        display: inline-block;
        cursor: pointer;
        overflow: hidden;
    }
    
    .file-upload input[type=file] {
        position: absolute;
        left: 0;
        top: 0;
        opacity: 0;
        width: 100%;
        height: 100%;
        cursor: pointer;
    }
    
    .file-upload-label {
        display: inline-block;
        padding: 10px 15px;
        background: rgba(59, 130, 246, 0.2);
        color: var(--info-blue);
        border-radius: 8px;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        white-space: nowrap;
    }
    
    .file-upload:hover .file-upload-label {
        background: rgba(59, 130, 246, 0.3);
    }
    
    /* Pricing Cards */
    .pricing-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
        gap: 30px; 
        margin-top: 40px; 
    }
    
    .pricing-card { 
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8)); 
        padding: 35px; 
        border-radius: 20px; 
        border: 1px solid rgba(220,38,38,0.2); 
        text-align: center; 
        transition: all .4s cubic-bezier(.4,0,.2,1);
        animation: fadeUp 0.6s ease forwards;
        opacity: 0;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .pricing-card:nth-child(1) { animation-delay: 0.1s; }
    .pricing-card:nth-child(2) { animation-delay: 0.2s; }
    .pricing-card:nth-child(3) { animation-delay: 0.3s; }
    
    .pricing-card.featured { 
        border: 2px solid var(--primary-red); 
        transform: scale(1.05);
        animation-delay: 0.2s;
    }
    
    .pricing-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(220,38,38,0.3);
    }
    
    /* Admin Table */
    .admin-users-table { 
        width: 100%; 
        overflow-x: auto; 
        margin-top: 20px; 
    }
    
    .admin-users-table table { 
        width: 100%; 
        border-collapse: collapse; 
        min-width: 840px; 
    }
    
    .admin-users-table th { 
        background: linear-gradient(135deg, rgba(220,38,38,0.1), rgba(220,38,38,0.05)); 
        color: var(--primary-red); 
        padding: 15px; 
        text-align: left; 
        font-weight: 600; 
        text-transform: uppercase; 
        font-size: .85rem; 
        letter-spacing: 1px; 
        border-bottom: 2px solid rgba(220,38,38,0.2); 
        white-space: nowrap;
    }
    
    .admin-users-table td { 
        padding: 15px; 
        border-bottom: 1px solid rgba(220,38,38,0.1); 
        color: var(--text-light); 
        font-size: .95rem; 
        word-break: break-word;
        overflow-wrap: break-word;
        max-width: 200px;
    }
    
    /* API Control Styles */
    .api-row {
        display: grid;
        grid-template-columns: 1fr 0.5fr 2.5fr 1.3fr 0.8fr;
        gap: 10px;
        align-items: center;
    }
    
    .api-row input[type=text] {
        width: 100%;
    }
    
    .toggle-pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        border: 1px solid rgba(255,255,255,0.12);
        cursor: pointer;
    }
    
    .toggle-on { background: rgba(34,197,94,0.2); color: var(--success-green); }
    .toggle-off { background: rgba(220,38,38,0.2); color: var(--primary-red); }
    
    /* Toast */
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(26,26,26,0.95);
        border: 1px solid rgba(220,38,38,0.2);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        z-index: 2000;
        opacity: 0;
        transform: translateY(20px);
        transition: all .3s ease;
        max-width: 320px;
    }
    
    .toast.show {
        opacity: 1;
        transform: translateY(0);
    }
    
    /* Email Verification Styles */
    .verification-container {
        max-width: 500px;
        margin: 100px auto;
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8));
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(220,38,38,0.2);
        backdrop-filter: blur(20px);
        text-align: center;
    }
    
    .firebase-verification {
        background: linear-gradient(135deg, rgba(26,26,26,0.95), rgba(26,26,26,0.8));
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(220,38,38,0.2);
        backdrop-filter: blur(20px);
        text-align: center;
        max-width: 600px;
        margin: 50px auto;
    }
    
    /* Sound Indicator */
    .sound-indicator {
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: rgba(26,26,26,0.8);
        border: 1px solid rgba(220,38,38,0.2);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-red);
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
    }
    
    .sound-indicator:hover {
        transform: scale(1.1);
        background: rgba(220,38,38,0.2);
    }
    
    .sound-indicator.muted {
        color: var(--text-gray);
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .container { padding: 10px; }
        .header h1 { font-size: 2rem; text-align: center; }
        .header { padding: 25px; }
        .tools-grid { grid-template-columns: 1fr; gap: 20px; }
        .search-form { flex-direction: column; }
        .credits-display, .user-info { position: static; margin-bottom: 20px; width: 100%; max-width: 100%; }
        .credits-display { flex-direction: row; justify-content: space-between; min-width: auto; }
        .user-info { justify-content: center; flex-wrap: wrap; }
        .pricing-grid { grid-template-columns: 1fr; }
        .pricing-card.featured { transform: scale(1); }
        .search-container { padding: 30px 20px; }
        .results-container { padding: 30px 20px; }
        .data-grid { grid-template-columns: 1fr; }
        .admin-users-table { overflow-x: scroll; }
        .result-item { flex-direction: column; align-items: flex-start; }
        .copy-btn { margin-left: 0; margin-top: 10px; }
        .api-row { grid-template-columns: 1fr; }
        .sound-indicator { bottom: 10px; left: 10px; }
    }
    
    @media (max-width: 480px) {
        .header h1 { font-size: 1.5rem; letter-spacing: 1px; }
        .tool-card { padding: 25px; }
        .search-btn { padding: 16px 24px; font-size: 0.9rem; }
        .btn { padding: 12px 20px; font-size: 0.9rem; }
        .user-info { padding: 10px 15px; gap: 10px; }
        .user-info a { padding: 6px 10px; font-size: 0.8rem; }
    }
</style>
'''

# Enhanced Global Script with Better Data Handling and API Protection + Sounds + Toast
GLOBAL_SCRIPT = '''
<script>
// Sound settings
let soundEnabled = true;
// Small beep sounds using WebAudio (no files needed)
function playSound(type) {
  if (!soundEnabled) return;
  
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.type = 'sine';
    if (type === 'success') o.frequency.value = 880;
    else if (type === 'error') o.frequency.value = 220;
    else o.frequency.value = 440;
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.08, ctx.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.18);
    o.start();
    o.stop(ctx.currentTime + 0.20);
  } catch(e) {}
}
// Toggle sound
function toggleSound() {
    soundEnabled = !soundEnabled;
    const indicator = document.getElementById('soundIndicator');
    if (indicator) {
        if (soundEnabled) {
            indicator.classList.remove('muted');
            indicator.innerHTML = '<i class="fas fa-volume-up"></i>';
            showToast('Sound enabled', 'success');
        } else {
            indicator.classList.add('muted');
            indicator.innerHTML = '<i class="fas fa-volume-mute"></i>';
            showToast('Sound disabled', 'success');
        }
    }
}
// Toast UI
function showToast(msg, type='info'){
  const t = document.getElementById('toast');
  if(!t) return;
  t.textContent = msg;
  t.style.borderColor = (type==='error') ? 'rgba(220,38,38,0.5)' : (type==='success'?'rgba(34,197,94,0.5)':'rgba(220,38,38,0.2)');
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), 2500);
}
// Format timestamp
function formatTimestamp(val){
  try{
    const n = Number(val);
    if(!Number.isFinite(n)) return null;
    const ms = (n > 1e12) ? n : (n > 1e9 ? n*1000 : null);
    if (!ms) return null;
    const d = new Date(ms);
    return isNaN(d) ? null : d.toLocaleString();
  } catch(e){ return null; }
}
// Escape HTML
function escapeHtml(s){ 
    return (''+s).replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m]));
}
// Convert value to display string
function toDisplayString(v){
  if (v === null || v === undefined) return '';
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  if (typeof v === 'number') {
    const ts = formatTimestamp(v);
    return ts || String(v);
  }
  if (typeof v === 'string') {
    const maybeNum = Number(v);
    if (!isNaN(maybeNum)) {
      const ts = formatTimestamp(maybeNum);
      if (ts) return ts;
    }
    return v;
  }
  return JSON.stringify(v, null, 2);
}
// Copy text with feedback
function copyText(text, btn){
  navigator.clipboard.writeText(text).then(() => {
    playSound('success');
    if(btn) {
      const originalText = btn.innerHTML;
      btn.innerHTML = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove('copied');
      }, 2000);
    }
  }).catch(()=>{});
}
// Filter out unwanted keys
function filterData(obj) {
  const unwantedKeys = ['dev', 'channel', '_resolved_region'];
  const filtered = {};
  for (const [key, value] of Object.entries(obj)) {
    if (!unwantedKeys.includes(key.toLowerCase())) {
      filtered[key] = value;
    }
  }
  return filtered;
}
// Render key-value pair
function renderKV(key, value){
  let valueType = typeof value;
  let display = toDisplayString(value);
  let isComplex = value && (valueType === 'object');
  
  if (['dev', 'channel'].includes(key.toLowerCase())) return '';
  
  let html = '<div class="result-item">';
  html += '<span style="color: var(--text-gray);">' + escapeHtml(key) + '</span>';
  
  if (isComplex){
    const filtered = filterData(value);
    html += '<span style="color: white; max-width: 70%; flex: 1; text-align: right;">'
         + '<details style="text-align:left;"><summary style="cursor:pointer; color: var(--info-blue);">View details (' 
         + (Array.isArray(value)? 'Array['+value.length+']':'Object') + ')</summary>'
         + '<pre style="margin-top:10px; white-space:pre-wrap; font-size:0.85rem; color: var(--text-gray);">' 
         + escapeHtml(JSON.stringify(filtered, null, 2)) + '</pre></details></span>';
    html += '<button class="copy-btn" onclick="copyText(' + JSON.stringify(JSON.stringify(filtered)) + ', this)">Copy</button>';
  } else {
    const disp = String(display);
    const pill = (typeof value === 'boolean')
      ? ('<span class="pill ' + (value?'pill-yes':'pill-no') + '">' + disp + '</span>')
      : escapeHtml(disp);
    html += '<span style="color: white; max-width:70%; text-align:right; word-break: break-word;">' + pill + '</span>';
    html += '<button class="copy-btn" onclick="copyText(' + JSON.stringify(disp) + ', this)">Copy</button>';
  }
  html += '</div>';
  return html;
}
// Render object with filtering
function renderObject(obj){
  let out = '';
  const filtered = filterData(obj);
  Object.entries(filtered).forEach(([k,v])=>{
    if (v !== null && v !== undefined && v !== '') {
      const kvHtml = renderKV(k, v);
      if (kvHtml) out += kvHtml;
    }
  });
  return out;
}
// Create data card for summary
function createDataCard(label, value) {
  return '<div class="data-card"><div class="data-label">' + escapeHtml(label) + '</div><div class="data-value">' + escapeHtml(value || '-') + '</div></div>';
}
// API Protection - Prevent network tab inspection (basic)
(function() {
    let devtools = {open: false, orientation: null};
    const threshold = 160;
    
    setInterval(function() {
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
            if (!devtools.open) {
                devtools.open = true;
                console.clear();
                console.log("%cDevTools detected! API endpoints are protected.", "color: red; font-size: 20px; font-weight: bold;");
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    const url = args[0];
                    if (typeof url === 'string' && url.includes('/api/')) {
                        console.log(`API call to ${url} detected and logged for security purposes.`);
                    }
                    return originalFetch.apply(this, args);
                };
            }
        } else {
            devtools.open = false;
        }
    }, 500);
})();
</script>
'''