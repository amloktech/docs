// Adapted from the AMLOK website brand system, version 2.0.0.
// Self-contained for Mintlify. Asset licenses: /brand/licenses.txt.
export const BrandGuidelines = () => {
let nextIllustrationId=0;
const useId=()=>{const [id]=useState(()=>`amlok-brand-${++nextIllustrationId}`);return id;};
const AlertTriangle=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3","key":"wmoenq"}],["path",{"d":"M12 9v4","key":"juzpu7"}],["path",{"d":"M12 17h.01","key":"p32p05"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const ArrowRight=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M5 12h14","key":"1ays0h"}],["path",{"d":"m12 5 7 7-7 7","key":"xquz4c"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Check=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M20 6 9 17l-5-5","key":"1gmf2c"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const FileText=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z","key":"1oefj6"}],["path",{"d":"M14 2v5a1 1 0 0 0 1 1h5","key":"wfsgrz"}],["path",{"d":"M10 9H8","key":"b1mrlr"}],["path",{"d":"M16 13H8","key":"t4e002"}],["path",{"d":"M16 17H8","key":"z1uh3a"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const ImageIcon=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["rect",{"width":"18","height":"18","x":"3","y":"3","rx":"2","ry":"2","key":"1m3agn"}],["circle",{"cx":"9","cy":"9","r":"2","key":"af1f0g"}],["path",{"d":"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21","key":"1xmnt7"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Loader2=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M21 12a9 9 0 1 1-6.219-8.56","key":"13zald"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Search=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"m21 21-4.34-4.34","key":"14j7rj"}],["circle",{"cx":"11","cy":"11","r":"8","key":"4ej97u"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const ShieldCheck=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z","key":"oel41y"}],["path",{"d":"m9 12 2 2 4-4","key":"dzmm74"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const ArrowDownLeft=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M17 7 7 17","key":"15tmo1"}],["path",{"d":"M17 17H7V7","key":"1org7z"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Banknote=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["rect",{"width":"20","height":"12","x":"2","y":"6","rx":"2","key":"9lu3g6"}],["circle",{"cx":"12","cy":"12","r":"2","key":"1c9p78"}],["path",{"d":"M6 12h.01M18 12h.01","key":"113zkx"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const CircleAlert=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["circle",{"cx":"12","cy":"12","r":"10","key":"1mglay"}],["line",{"x1":"12","x2":"12","y1":"8","y2":"12","key":"1pkeuh"}],["line",{"x1":"12","x2":"12.01","y1":"16","y2":"16","key":"4dfq90"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const UserRound=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["circle",{"cx":"12","cy":"8","r":"5","key":"1hypcn"}],["path",{"d":"M20 21a8 8 0 0 0-16 0","key":"rfgkzh"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const CheckCheck=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M18 6 7 17l-5-5","key":"116fxf"}],["path",{"d":"m22 10-7.5 7.5L13 16","key":"ke71qq"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Copy=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["rect",{"width":"14","height":"14","x":"8","y":"8","rx":"2","ry":"2","key":"17jyea"}],["path",{"d":"M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2","key":"zix9uf"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Download=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M12 15V3","key":"m9g1x1"}],["path",{"d":"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4","key":"ih7n3h"}],["path",{"d":"m7 10 5 5 5-5","key":"brsn70"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Layers3=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z","key":"zw3jo"}],["path",{"d":"M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12","key":"1wduqc"}],["path",{"d":"M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17","key":"kqbvx6"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Menu=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M4 5h16","key":"1tepv9"}],["path",{"d":"M4 12h16","key":"1lakjw"}],["path",{"d":"M4 19h16","key":"1djgab"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Moon=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401","key":"kfwtm"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Pause=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["rect",{"x":"14","y":"3","width":"5","height":"18","rx":"1","key":"kaeet6"}],["rect",{"x":"5","y":"3","width":"5","height":"18","rx":"1","key":"1wsw3u"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Play=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z","key":"10ikf1"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Radio=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M16.247 7.761a6 6 0 0 1 0 8.478","key":"1fwjs5"}],["path",{"d":"M19.075 4.933a10 10 0 0 1 0 14.134","key":"ehdyv1"}],["path",{"d":"M4.925 19.067a10 10 0 0 1 0-14.134","key":"1q22gi"}],["path",{"d":"M7.753 16.239a6 6 0 0 1 0-8.478","key":"r2q7qm"}],["circle",{"cx":"12","cy":"12","r":"2","key":"1c9p78"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const ScanLine=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M3 7V5a2 2 0 0 1 2-2h2","key":"aa7l1z"}],["path",{"d":"M17 3h2a2 2 0 0 1 2 2v2","key":"4qcy5o"}],["path",{"d":"M21 17v2a2 2 0 0 1-2 2h-2","key":"6vwrx8"}],["path",{"d":"M7 21H5a2 2 0 0 1-2-2v-2","key":"ioqczr"}],["path",{"d":"M7 12h10","key":"b7w52i"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const Sun=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["circle",{"cx":"12","cy":"12","r":"4","key":"4exip2"}],["path",{"d":"M12 2v2","key":"tus03m"}],["path",{"d":"M12 20v2","key":"1lh1kg"}],["path",{"d":"m4.93 4.93 1.41 1.41","key":"149t6j"}],["path",{"d":"m17.66 17.66 1.41 1.41","key":"ptbguv"}],["path",{"d":"M2 12h2","key":"1t8f8n"}],["path",{"d":"M20 12h2","key":"1q8mjw"}],["path",{"d":"m6.34 17.66-1.41 1.41","key":"1m8zz5"}],["path",{"d":"m19.07 4.93-1.41 1.41","key":"1shlcs"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const X=({size=24,strokeWidth=2,...props})=><svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{[["path",{"d":"M18 6 6 18","key":"1bl5f8"}],["path",{"d":"m6 6 12 12","key":"d8bk6v"}]].map(([Tag,attrs])=><Tag {...attrs}/>)}</svg>;
const brand = {
    name: 'AMLOK', version: '2.0.0', reviewed: '2026-10-23',
    principle: 'Clear by design. Connected by signals.',
};
/** The existing hero field, shared by CSS surfaces and SVG illustration fills. */
const heroGradientStops = [
    { offset: 0, color: 'var(--blue-deep)' },
    { offset: .42, color: 'var(--hero-blue-middle)' },
    { offset: 1, color: 'var(--identity-blue)' },
];
const heroGradient = {
    name: 'AMLOK hero gradient',
    token: '--gradient-hero',
    css: `radial-gradient(ellipse at 50% 42%, ${heroGradientStops.map(stop => `${stop.color} ${stop.offset * 100}%`).join(', ')})`,
    stops: heroGradientStops,
    // CSS farthest-corner ellipse in SVG object-bounding-box coordinates.
    svgTransform: 'translate(0.5 0.42) scale(0.7071067812 0.8202438662)',
};
/** Shared AMLOK marketing layout. */
const siteLayout = { contentMax: 1280, desktopGutter: 48, compactGutter: 20, desktopBreakpoint: 1024 };
/** Source of truth for the site and the downloadable design tokens. */
const tokenGroups = {
    Color: {
        '--canvas': '#ffffff', '--ink': '#101828', '--surface': '#f5f7fb',
        '--surface-raised': '#ffffff', '--line': '#d7deeb', '--line-strong': '#8290a8',
        '--muted': '#58657b', '--identity-blue': '#052698', '--blue': 'var(--identity-blue)', '--blue-secondary': '#2567ff',
        '--blue-secondary-hover': '#174fc9', '--blue-deep': '#1b4fe0', '--blue-soft': '#eaf1ff',
        '--blue-field': '#1239b0', '--navy': 'var(--blue-field)',
        '--hero-blue-middle': '#1140c3',
        '--on-brand': '#ffffff',
        '--on-brand-muted': 'color-mix(in srgb, var(--on-brand) 85%, var(--blue-field))',
        '--on-brand-line': 'color-mix(in srgb, var(--on-brand) 24%, transparent)',
        '--on-brand-surface': 'color-mix(in srgb, var(--on-brand) 8%, transparent)',
        '--signal-violet': '#7b3ff2', '--signal-violet-soft': '#f2ebff',
        '--signal-orange': '#f15a24', '--signal-orange-soft': '#fff0e8',
        '--signal-green': '#41b978', '--signal-green-soft': '#e8f6ee',
        '--success-bg': '#e8f6ee', '--success-fg': '#087b46',
        '--warning-bg': '#fff7e0', '--warning-fg': '#815600',
        '--danger-bg': '#fff0f0', '--danger-fg': '#b42336',
        '--action-fill': '#052698', '--action-ink': '#ffffff', '--focus': '#2567ff',
    },
    Gradient: {
        '--gradient-hero': heroGradient.css,
    },
    Geometry: {
        '--radius-xs': '4px', '--radius-sm': '8px', '--radius-control': '10px',
        '--radius-inner': '12px', '--radius-card': '20px', '--radius-panel': '24px',
        '--radius-media': '20px', '--radius-overlay': '16px', '--radius-pill': '999px', '--radius-signal': '50%',
        '--border-width': '1px', '--focus-width': '2px',
    },
    Surfaces: {
        '--shadow-color': '#101828',
        '--border-subtle': 'color-mix(in srgb, var(--ink) 8%, transparent)',
        '--border-default': 'color-mix(in srgb, var(--ink) 12%, transparent)',
        '--edge-inset': 'inset 0 0 0 1px var(--border-subtle)',
        '--shadow-button': '0 1px 2px color-mix(in srgb, var(--shadow-color) 6%, transparent)',
        '--shadow-raised': '0 2px 4px color-mix(in srgb, var(--shadow-color) 3%, transparent), 0 12px 32px color-mix(in srgb, var(--shadow-color) 5%, transparent)',
        '--shadow-overlay': '0 4px 12px color-mix(in srgb, var(--shadow-color) 6%, transparent), 0 24px 64px color-mix(in srgb, var(--shadow-color) 12%, transparent)',
        '--shadow-navigation': '0 4px 24px color-mix(in srgb, var(--shadow-color) 4%, transparent)',
    },
    Layout: {
        '--site-content-max': `${siteLayout.contentMax}px`,
        '--site-min-gutter': `${siteLayout.desktopGutter}px`,
        '--site-gutter': 'max(var(--site-min-gutter), calc((100vw - var(--site-content-max)) / 2))',
        '--site-content-width': 'min(var(--site-content-max), calc(100vw - var(--site-gutter) - var(--site-gutter)))',
        '--page-max': '1200px', '--section-gap': '64px', '--space-section': 'clamp(64px, 7vw, 112px)',
        '--space-section-content': '48px', '--space-heading-body': '24px', '--space-copy-actions': '24px',
        '--space-actions-media': '32px', '--space-media-caption': '16px', '--space-card-gap': '24px',
        '--space-card-inset': '24px', '--media-panel-height': '240px', '--control-height': '44px',
        '--control-height-compact': '40px', '--control-height-marketing': '48px', '--reading-width': '65ch',
    },
    Typography: {
        '--font-sans': "'Inter Variable', Inter, ui-sans-serif, system-ui, sans-serif",
        '--font-mono': "'JetBrains Mono Variable', ui-monospace, monospace",
        '--text-section-heading': 'clamp(36px, 4.4vw, 62px)',
        '--text-section-description': 'clamp(16px, 1.25vw, 18px)',
        '--text-risk-card-title': 'clamp(18px, 2vw, 28px)',
        '--text-body': '16px', '--text-secondary': '14px', '--text-label': '12px',
        '--leading-body': '1.6', '--leading-heading': '1.08',
    },
    Motion: {
        '--motion-fast': '150ms', '--motion-base': '200ms', '--motion-slow': '400ms',
        '--motion-scan': '4000ms', '--ease-out': 'cubic-bezier(.16, 1, .3, 1)',
    },
    Layers: {
        '--z-dropdown': '20', '--z-sticky': '30', '--z-navigation': '40',
        '--z-overlay': '50', '--z-notification': '80', '--z-access': '100',
    },
};
const darkTokens = {
    '--shadow-color': '#000000',
    '--canvas': '#09162d', '--ink': '#f4f7ff', '--surface': '#101f38', '--surface-raised': '#162740',
    '--line': '#33445f', '--line-strong': '#7184a3', '--muted': '#b4c2d8',
    '--blue': '#9cbaff', '--blue-soft': '#182e58', '--action-fill': '#a9c3ff',
    '--action-ink': 'var(--blue-field)', '--focus': '#9cbaff',
    '--success-bg': '#11372b', '--success-fg': '#8ce0af',
    '--warning-bg': '#3d3012', '--warning-fg': '#f4d17a',
    '--danger-bg': '#451d2b', '--danger-fg': '#ffadba',
};
const colors = [
    { name: 'AMLOK blue', hex: '#052698', token: '--blue', use: 'Identity, primary actions, trusted structure', light: false },
    { name: 'Signal blue', hex: '#2567FF', token: '--blue-secondary', use: 'Focus, selected signals, chart emphasis', light: false },
    { name: 'Cobalt blue', hex: tokenGroups.Color['--blue-field'].toUpperCase(), token: '--blue-field', use: 'Blue brand panels, reversed identity, and signal fields', light: false },
    { name: 'Canvas', hex: '#FFFFFF', token: '--canvas', use: 'Primary reading and decision surfaces', light: true },
    { name: 'Surface', hex: '#F5F7FB', token: '--surface', use: 'Secondary regions and image placeholders', light: true },
    { name: 'Ink', hex: '#101828', token: '--ink', use: 'Headings, values, and primary text', light: false },
    { name: 'Insight violet', hex: '#7B3FF2', token: '--signal-violet', use: 'Simulation and distinct chart series', light: false },
    { name: 'Attention orange', hex: '#F15A24', token: '--signal-orange', use: 'Attention markers; use semantic text colors', light: true },
    { name: 'Signal green', hex: '#41B978', token: '--signal-green', use: 'Live or positive markers; always labeled', light: true },
];
const declarations = (tokens) => Object.entries(tokens).map(([key, value]) => `  ${key}: ${value};`).join('\n');
const tokensCSS = `/* AMLOK ${brand.version} - Rounded surfaces / Precise graphics / Clear signals. Source: /brand */
:root {
${Object.values(tokenGroups).map(declarations).join('\n')}
}
[data-amlok-theme="dark"] {
${declarations(darkTokens)}
}
@media (max-width: ${siteLayout.desktopBreakpoint - 1}px) { :root { --site-min-gutter: ${siteLayout.compactGutter}px; } }
@media (prefers-reduced-motion: reduce) {
  :root { --motion-fast: 0ms; --motion-base: 0ms; --motion-slow: 0ms; }
}
`;

function Mark({ className = '' }) {
    return <svg className={className} width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M3 26 13 6h6l10 20h-7L16 13l-3.5 7H19l3 6H3Z" fill="currentColor"/></svg>;
}
function Wordmark({ className = '' }) {
    return <span className={`wordmark ${className}`}><Mark /><span>amlok</span></span>;
}

function Status({ children, tone = 'blue' }) {
    return <span className={`ds-status ds-status-${tone}`}><i aria-hidden="true"/>{children}</span>;
}
function ShieldGraphic() {
    return <svg viewBox="0 0 200 220" className="ds-shield" aria-hidden="true"><path d="M24 24H176V136L100 196 24 136Z" fill="none" stroke="currentColor" strokeWidth="2"/><path d="M38 38H162V128L100 177 38 128Z" fill="currentColor" opacity=".08"/><g transform="translate(60 60) scale(2.5)"><path d="M3 26 13 6h6l10 20h-7L16 13l-3.5 7H19l3 6H3Z" fill="currentColor"/></g><path d="M16 44V16H44M156 16H184V44M16 116V144L36 160M164 160L184 144V116" fill="none" stroke="currentColor" opacity=".35"/></svg>;
}
function RadarVisual({ paused = false, label = 'AMLOK / SIGNAL FIELD' }) {
    const ref = useRef(null);
    const [inView, setInView] = useState(false);
    useEffect(() => {
        const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: .15 });
        if (ref.current)
            observer.observe(ref.current);
        return () => observer.disconnect();
    }, []);
    return <div ref={ref} className="ds-radar" data-running={inView && !paused} role="img" aria-label="A geometric shield within a square scanning field, with connected signal points">
    <div className="ds-radar-grid"/><div className="ds-radar-frame ds-frame-outer"/><div className="ds-radar-frame ds-frame-middle"/><div className="ds-radar-frame ds-frame-inner"/>
    <svg className="ds-radar-network" viewBox="0 0 600 420" preserveAspectRatio="none" aria-hidden="true"><path d="M58 276H144V132H270V210H412V82H540M144 276H390V330H510M270 132V58M412 210H542" fill="none" stroke="currentColor" strokeWidth="1"/>{[[58, 276], [144, 132], [270, 58], [412, 82], [540, 82], [390, 330], [510, 330], [542, 210]].map(([x, y], i) => <g key={i} fill="currentColor"><circle cx={x} cy={y} r="12" opacity=".12"/><circle cx={x} cy={y} r="4"/></g>)}</svg>
    <div className="ds-scan"/><ShieldGraphic /><span className="ds-radar-caption">{label}</span><span className="ds-radar-coordinate">N 04 / E 08</span>
  </div>;
}
function MediaPlaceholder({ label = 'Image placeholder' }) {
    return <div className="ds-media-placeholder" role="img" aria-label={label}><ImageIcon size={24} aria-hidden="true"/><span>{label}</span><i aria-hidden="true"/></div>;
}
function ComponentLab({ onOpen, onNotice }) {
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [enabled, setEnabled] = useState(true);
    const [tab, setTab] = useState(0);
    const [saved, setSaved] = useState(false);
    const tabs = ['Overview', 'Evidence', 'Activity'];
    return <>
    <div className="ds-grid ds-grid-2">
      <article className="ds-panel"><span className="ds-meta">ACTIONS / ROUNDED CONTROLS</span><h3>One primary action.</h3><div className="ds-button-samples"><button className="ds-button" onClick={onOpen}>Review decision <ArrowRight size={16}/></button><button className="ds-button ds-button-secondary" onClick={() => onNotice('Secondary action preview activated')}>View evidence</button><button className="ds-button ds-button-quiet" onClick={() => onNotice('Text action preview activated')}>Export record <ArrowRight size={16}/></button><button className="ds-button" disabled>Unavailable</button><button className="ds-button ds-button-secondary" disabled aria-busy="true"><Loader2 size={16}/>Saving…</button></div><p className="ds-note">44px default height · 16–24px horizontal inset · 8px icon gap. A filled blue primary, an outlined secondary, and an unboxed tertiary. Focus remains outside the control boundary.</p></article>
      <form className="ds-panel ds-form" noValidate onSubmit={e => { e.preventDefault(); if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setError('Enter a valid work email, for example alex@company.ca.');
        setSaved(false);
        return;
    } setError(''); setSaved(true); }}>
        <span className="ds-meta">FIELDS / VALIDATION / PREFERENCES</span><label htmlFor="ds-email">Work email <span>(required)</span></label><input id="ds-email" type="email" autoComplete="email" value={email} placeholder="alex@company.ca" aria-invalid={!!error} aria-describedby={error ? 'ds-email-error' : 'ds-email-hint'} onChange={e => { setEmail(e.target.value); setError(''); setSaved(false); }}/><p id="ds-email-hint" className="ds-note">Used for this local component preview only.</p>{error && <p className="ds-field-error" id="ds-email-error" role="alert"><AlertTriangle size={16}/>{error}</p>}
        <label className="ds-checkbox"><input type="checkbox" defaultChecked/>Include source links in the review</label><div className="ds-switch-row"><span id="ds-switch-label">Signal notifications</span><button className="ds-switch" type="button" role="switch" aria-checked={enabled} aria-labelledby="ds-switch-label" onClick={() => setEnabled(!enabled)}><span /></button></div><button className="ds-button ds-button-secondary" type="submit">Save preference <Check size={16}/></button><p className="ds-note" role="status">{saved ? 'Preference saved for this preview.' : ''}</p>
      </form>
    </div>
    <div className="ds-panel ds-tabs-demo"><div className="ds-tabs" role="tablist" aria-label="Record preview">{tabs.map((item, index) => <button key={item} role="tab" id={`ds-tab-${index}`} aria-controls={`ds-tab-panel-${index}`} aria-selected={index === tab} tabIndex={index === tab ? 0 : -1} onClick={() => setTab(index)} onKeyDown={e => { const next = e.key === 'ArrowRight' ? (index + 1) % 3 : e.key === 'ArrowLeft' ? (index + 2) % 3 : e.key === 'Home' ? 0 : e.key === 'End' ? 2 : null; if (next !== null) {
        e.preventDefault();
        setTab(next);
        document.getElementById(`ds-tab-${next}`)?.focus();
    } }}>{item}</button>)}</div><div className="ds-tab-panel" id={`ds-tab-panel-${tab}`} role="tabpanel" aria-labelledby={`ds-tab-${tab}`} tabIndex={0}><ShieldCheck size={22}/><div><h3>{['A complete view of the file', 'Evidence stays within reach', 'A traceable sequence'][tab]}</h3><p>{['Use tabs for sibling views. Keep the selected state visible with an underline and a change in text weight.', 'Show source, date, owner, and freshness beside each relevant fact.', 'Display who changed what and when, with a path back to the original evidence.'][tab]}</p></div></div></div>
  </>;
}
const records = [
    { name: 'Northstar Foods', id: 'EX-1042', stage: 'Underwriting', status: 'In review', exposure: '$240,000', source: 'Financial statements · 30 Sep 2026', tone: 'warning' },
    { name: 'Cedar Logistics', id: 'EX-1043', stage: 'Monitoring', status: 'Current', exposure: '$180,000', source: 'Transaction feed · 20 Oct 2026', tone: 'success' },
    { name: 'Harbour Supply', id: 'EX-1044', stage: 'Verification', status: 'Needs evidence', exposure: '$320,000', source: 'Ownership declaration · 18 Oct 2026', tone: 'danger' },
];
function DataWorkspace() {
    const [query, setQuery] = useState('');
    const [sort, setSort] = useState(false);
    const [selected, setSelected] = useState(records[0]);
    const [restored, setRestored] = useState(false);
    const rows = records.filter(r => `${r.name} ${r.status} ${r.stage}`.toLowerCase().includes(query.toLowerCase())).sort((a, b) => sort ? b.name.localeCompare(a.name) : a.name.localeCompare(b.name));
    return <>
    <div className="ds-workspace"><div className="ds-workspace-bar"><span><Mark />Credit workspace</span><Status tone="neutral">Illustrative data</Status></div><div className="ds-workspace-toolbar"><label className="ds-search"><Search size={18}/><input type="search" aria-label="Search sample borrowers" placeholder="Search borrowers or status" value={query} onChange={e => setQuery(e.target.value)}/></label><span className="ds-meta">{rows.length} RECORDS</span></div>
      <div className="ds-workspace-body"><div className="ds-table-scroll" role="region" tabIndex={0} aria-label="Sample borrower table"><table className="ds-table"><thead><tr><th aria-sort={sort ? 'descending' : 'ascending'}><button onClick={() => setSort(!sort)}>Borrower {sort ? '↓' : '↑'}</button></th><th>Workflow</th><th>Status</th><th className="ds-numeric">Exposure</th></tr></thead><tbody>{rows.map(row => <tr key={row.id} data-selected={selected.id === row.id}><td><button className="ds-record-link" onClick={() => setSelected(row)} aria-label={`View evidence for ${row.name}`}>{row.name}</button><small>{row.id}</small></td><td>{row.stage}</td><td><Status tone={row.tone}>{row.status}</Status></td><td className="ds-numeric">{row.exposure}</td></tr>)}</tbody></table>{!rows.length && <div className="ds-empty"><Search size={24}/><h4>No matching borrowers</h4><p>Try a name, workflow, or status.</p><button className="ds-button ds-button-secondary" onClick={() => setQuery('')}>Clear search</button></div>}</div>
      <aside className="ds-evidence" aria-live="polite"><span className="ds-meta">EVIDENCE / SELECT A RECORD</span><h3>{selected.name}</h3><Status tone={selected.tone}>{selected.status}</Status><div className="ds-evidence-source"><FileText size={18}/><span>{selected.source}<small>Example source · not a customer record</small></span></div><p>Keep the evidence beside the decision. The full record and its history stay available.</p></aside></div>
    </div>
    <div className="ds-grid ds-grid-3 ds-state-grid"><article className="ds-panel"><Loader2 size={22}/><h3>Loading</h3><div className="ds-skeleton"/><div className="ds-skeleton ds-skeleton-short"/><p>Reserve the final layout. Show progress text for work that takes time. Offer cancellation for long tasks.</p></article><article className="ds-panel"><FileText size={22}/><h3>Empty</h3><p>No evidence has been added. Explain what belongs here and offer a specific next step.</p><span className="ds-meta">ACTION: ADD DOCUMENTS</span></article><article className="ds-panel"><AlertTriangle size={22}/><h3>{restored ? 'Recovered' : 'Connection interrupted'}</h3><p role="status">{restored ? 'The preview connection is restored. Preserve the user’s filters and selection.' : 'Keep the previous result visible with a stale-data label. Explain the recovery action.'}</p><button className="ds-button ds-button-secondary" onClick={() => setRestored(!restored)}>{restored ? 'Reset example' : 'Retry preview'}</button></article></div>
  </>;
}
function ChartSpecimen() {
    return <div className="ds-chart-specimen"><div className="ds-chart-heading"><div><span className="ds-meta">ILLUSTRATIVE PORTFOLIO / CAD</span><h3>Exposure by workflow</h3></div><span className="ds-note">Snapshot · 20 Oct 2026</span></div><div className="ds-chart" role="img" aria-label="Example exposure: Verification 32%, Underwriting 48%, Monitoring 72%, Servicing 40%">{[['Verification', 32], ['Underwriting', 48], ['Monitoring', 72], ['Servicing', 40]].map(([name, value]) => <div key={name}><span>{name}</span><div><i style={{ width: `${value}%` }}/></div><strong>{value}%</strong></div>)}</div><p className="ds-note">Direct labels, visible units, a consistent baseline, and square bars. Use a table alternative for precise values; never imply that a risk signal is a probability unless it is calibrated.</p></div>;
}
function FieldPatterns() {
    const [reviewType, setReviewType] = useState('Standard review');
    const [note, setNote] = useState('');
    const [density, setDensity] = useState('Comfortable');
    return <div className="ds-grid ds-grid-2 ds-field-patterns">
    <div className="ds-panel ds-form"><span className="ds-meta">CHOICE / CONTEXT / READ-ONLY</span>
      <label htmlFor="ds-review-type">Review workflow</label>
      <select id="ds-review-type" value={reviewType} onChange={e => setReviewType(e.target.value)}><option>Standard review</option><option>Enhanced review</option><option>Policy exception review</option></select>
      <label htmlFor="ds-record-id">Record ID</label><input id="ds-record-id" value="EX-1042" readOnly aria-describedby="ds-readonly-hint"/>
      <p id="ds-readonly-hint" className="ds-note">Read-only values stay selectable and readable. Disabled fields are reserved for unavailable actions.</p>
      <fieldset className="ds-radio-group"><legend>Workspace density</legend>{['Comfortable', 'Compact'].map(value => <label key={value}><input type="radio" name="ds-density" value={value} checked={density === value} onChange={() => setDensity(value)}/><span>{value}</span></label>)}</fieldset>
    </div>
    <div className="ds-panel ds-form"><span className="ds-meta">LONG-FORM INPUT / AUDIT CONTEXT</span>
      <label htmlFor="ds-review-note">Reviewer note <span>(optional)</span></label>
      <textarea id="ds-review-note" rows={5} maxLength={400} value={note} onChange={e => setNote(e.target.value)} aria-describedby="ds-review-note-hint" placeholder="Explain the evidence or policy consideration behind this review."/>
      <p id="ds-review-note-hint" className="ds-note">Keep personal data out of this example. {note.length}/400 characters.</p>
      <div className="ds-field-summary"><Status tone="neutral">{reviewType}</Status><p>Describe what changed, why it matters, and who should act next. A field’s label remains visible after a value is entered.</p></div>
    </div>
  </div>;
}

function ApprovalGraphic() {
    const id = useId().replace(/:/g, '');
    return <div className="adoption-approval"><div className="adoption-telemetry">Credit assessment</div><div className="adoption-legend"><span><i />Approved</span><span><i />Further review</span></div><svg viewBox="0 0 320 224" fill="none"><defs><pattern id={`approval-${id}`} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0V6" stroke="var(--blue)" strokeWidth="2"/></pattern></defs><circle cx="160" cy="111" r="78" stroke="var(--line)" strokeWidth="17"/><circle className="adoption-ring" cx="160" cy="111" r="78" stroke="var(--blue-secondary)" strokeWidth="17" pathLength="100" strokeDasharray="58 42" transform="rotate(-90 160 111)"/><circle cx="160" cy="111" r="78" stroke={`url(#approval-${id})`} strokeWidth="17" pathLength="100" strokeDasharray="12 88" strokeDashoffset="-58" transform="rotate(-90 160 111)"/><text x="160" y="115" textAnchor="middle" fill="var(--muted)" fontSize="11">APPROVAL REVIEW</text></svg><div className="adoption-graphic-note"><span className="adoption-hatched-key"/>Additional cash flow context</div></div>;
}
function RadarGraphic() {
    return <div className="adoption-radar"><div className="adoption-radar-grid"/><div className="adoption-radar-frame"><i /><i /><i /><b className="adoption-radar-cross horizontal"/><b className="adoption-radar-cross vertical"/><span className="adoption-radar-point point-one"/><span className="adoption-radar-point point-two"/><span className="adoption-radar-point point-alert"/><span className="adoption-radar-scan"/></div><span className="adoption-radar-label adoption-telemetry">Signal scan / active</span></div>;
}
function FraudGraphic() {
    return <div className="adoption-fraud"><div className="adoption-flags"><span><CircleAlert size={13}/>Signals for review</span><ul><li>Cash reserves declining</li><li>Revenue evidence incomplete</li><li>Concurrent borrowing detected</li></ul></div><div className="adoption-telemetry">Borrower file / 024</div><div className="adoption-mini-file"><strong>Business credit</strong><span>Institution: Example lender</span><span>Requested: CAD 85,000</span><span>Term: 24 months</span></div></div>;
}
function IncomeGraphic() {
    return <div className="adoption-income"><div className="adoption-deposit"><Banknote size={18}/><div><strong>Operating revenue</strong><small>Oct 15 · recurring deposit</small></div><b>+$12,480</b></div><div className="adoption-deposit secondary"><ArrowDownLeft size={16}/><div><strong>Contract payment</strong><small>Oct 08 · verified source</small></div><b>+$3,250</b></div><div className="adoption-income-bars">{[88, 62, 73, 91, 69, 82].map((height, i) => <i className={i > 2 ? 'projected' : ''} key={i} style={{ '--bar-height': `${height}%`, '--bar-delay': `${i * 100}ms` }}/>)}</div><div className="adoption-axis"><span>Observed income</span><span>Expected pattern</span></div></div>;
}
function OffersGraphic() {
    return <div className="adoption-offers"><div className="adoption-capacity"><span>Repayment capacity</span><div className="adoption-capacity-track">{Array.from({ length: 8 }, (_, i) => <i key={i}/>)}<b /></div><div className="adoption-axis"><span>Lower</span><span>Higher</span></div></div><div className="adoption-offer-file"><span className="adoption-telemetry">Offer scenario</span><div className="adoption-offer-tags"><span>For review</span><span><Check size={11}/>Policy aligned</span></div><strong>Working capital</strong><div><span>Principal</span><b>CAD 60,000</b></div><div><span>Term</span><b>18 months</b></div></div></div>;
}
function PortfolioGraphic() {
    return <div className="adoption-portfolio"><div className="adoption-telemetry">Liquidity / last six months</div><svg viewBox="0 0 320 215" fill="none">{[30, 65, 100, 135, 170, 205].map(y => <path key={y} d={`M12 ${y}H308`} stroke="var(--line)"/>)}<path className="adoption-trend" d="M12 85C45 85 51 72 80 76S122 64 153 67S190 62 210 79S259 108 308 144" stroke="var(--blue-secondary)" strokeWidth="2.5" pathLength="100"/><circle className="adoption-trend-point" cx="308" cy="144" r="4" fill="var(--signal-orange)"/></svg><div className="adoption-trend-alert"><CircleAlert size={12}/>Cash buffer declining</div><div className="adoption-axis"><span>May</span><span>October</span></div></div>;
}
function CollectionsGraphic() {
    return <div className="adoption-collections"><div className="adoption-code"><pre>{`{\n  "borrower": "example_024",\n  "cash_inflow": 12480.00,\n  "currency": "CAD",\n  "next_deposit": "Oct 30",\n  "payment_status": "review"\n}\n\n{\n  "workflow": "repayment",\n  "next_step": "contact",\n  "approval": "required"\n}`}</pre></div><div className="adoption-person"><UserRound size={36} strokeWidth={1.4}/></div><span className="adoption-collections-tag"><Check size={12}/>Human-approved workflow</span></div>;
}
function WebsiteGraphic({ kind }) {
    switch (kind) {
        case 'approvals': return <ApprovalGraphic />;
        case 'radar': return <RadarGraphic />;
        case 'fraud': return <FraudGraphic />;
        case 'income': return <IncomeGraphic />;
        case 'offers': return <OffersGraphic />;
        case 'portfolio': return <PortfolioGraphic />;
        case 'collections': return <CollectionsGraphic />;
    }
}

const specimens = [
    { kind: 'income', label: 'Cash flow', title: 'Evidence becomes a pattern.', description: 'Use transaction rows and a simple bar chart to connect individual deposits to recurring income.', construction: 'Square evidence rows sit above a shared baseline. Solid bars show observed activity; hatched bars distinguish an expected pattern.', motion: 'Bars rise subtly from their baseline over a 5-second loop. Labels and transaction values stay still.', alternative: 'Sample operating revenue and contract payments above six bars; the final three bars are hatched to indicate an expected pattern.' },
    { kind: 'radar', label: 'Signal scan', title: 'Make discovery visible.', description: 'Use a scanning field to explain how AMLOK brings emerging signals into focus.', construction: 'Nested rectangular frames, fine crosshairs, and small signal dots. One orange point introduces attention without turning the whole field into an alarm.', motion: 'A linear scan crosses the field over 5 seconds. Dots change opacity gently; nothing spins or flashes.', alternative: 'A square scanning field with nested frames, two blue signal dots, and one orange attention marker.' },
    { kind: 'portfolio', label: 'Trend', title: 'Show the change that matters.', description: 'Use one line and a labeled endpoint to explain movement across a defined period.', construction: 'A restrained grid, a blue trend line, and a single attention marker. Keep the time range and the interpretation beside the graphic.', motion: 'The line draws, holds, and resets over 7 seconds. The period and “Cash buffer declining” label remain visible.', alternative: 'An illustrative six-month liquidity trend with a declining endpoint and the label Cash buffer declining.' },
    { kind: 'offers', label: 'Capacity', title: 'Connect a signal to a review.', description: 'Use a segmented scale and a compact scenario card to show how evidence informs lending terms.', construction: 'A linear capacity scale, a clear indicator, and aligned label-value rows. Review and policy states use labeled semantic colors.', motion: 'The indicator moves gently within the scale over 6 seconds. The offer, amounts, and review labels remain stable.', alternative: 'A repayment capacity scale above a sample working capital offer of CAD 60,000 over 18 months, marked For review and Policy aligned.' },
    { kind: 'approvals', label: 'Assessment', title: 'Explain the fuller picture.', description: 'Use a ring only when the composition or proportion is the story. The surrounding interface uses the shared rounded surface system.', construction: 'One blue arc, a neutral remainder, and a hatched segment with a legend. A circular chart is a data shape, not a new card shape.', motion: 'The emphasized arc shifts slowly over 6 seconds. This is a conceptual illustration, not a changing approval rate.', alternative: 'A conceptual credit-assessment ring using a blue arc, a hatched segment, and a neutral remainder to show additional cash flow context.' },
    { kind: 'fraud', label: 'Review signals', title: 'Keep the evidence in context.', description: 'Use a short, labeled review list beside a borrower file to explain why a person should investigate.', construction: 'One warning surface, an outline icon, and specific evidence gaps. Describe what needs review without labeling a borrower as fraudulent.', motion: 'Only the review border changes emphasis over 6 seconds. The evidence remains legible throughout.', alternative: 'A sample borrower file with three review signals: declining reserves, incomplete revenue evidence, and concurrent borrowing.' },
    { kind: 'collections', label: 'Workflow', title: 'Connect intelligence to action.', description: 'Use a structured data field and a human-centered symbol to explain an approved operational workflow.', construction: 'Monospace sample data sits behind a square person tile. A persistent label makes human approval explicit.', motion: 'Background sample data travels slowly over 14 seconds. The person tile and approval label stay fixed.', alternative: 'Illustrative repayment data behind a person icon in a square frame, labeled Human-approved workflow.' },
];
function BrandGraphics() {
    const [selected, setSelected] = useState(0);
    const [inView, setInView] = useState(false);
    const previewRef = useRef(null);
    const tabRefs = useRef([]);
    const specimen = specimens[selected];
    useEffect(() => {
        const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: .1 });
        if (previewRef.current)
            observer.observe(previewRef.current);
        return () => observer.disconnect();
    }, []);
    return <div className="ds-graphics-library">
    <div className="ds-graphics-library-heading"><span className="ds-meta"><i />WEBSITE GRAPHICS / LIVE REFERENCE</span><a href="#website-graphics">Graphic library <ArrowRight size={16}/></a></div>
    <div className="ds-graphics-tabs" role="tablist" aria-label="Website graphic examples">
      {specimens.map((item, index) => <button key={item.kind} ref={node => { tabRefs.current[index] = node; }} type="button" role="tab" id={`graphic-tab-${item.kind}`} aria-controls="website-graphic-panel" aria-selected={selected === index} tabIndex={selected === index ? 0 : -1} onClick={() => setSelected(index)} onKeyDown={event => {
                const next = event.key === 'ArrowRight' ? (index + 1) % specimens.length : event.key === 'ArrowLeft' ? (index - 1 + specimens.length) % specimens.length : event.key === 'Home' ? 0 : event.key === 'End' ? specimens.length - 1 : null;
                if (next !== null) {
                    event.preventDefault();
                    setSelected(next);
                    tabRefs.current[next]?.focus();
                }
            }}>{item.label}</button>)}
    </div>
    <div className="ds-graphics-example" role="tabpanel" id="website-graphic-panel" aria-labelledby={`graphic-tab-${specimen.kind}`} tabIndex={0}>
      <figure className="ds-graphics-figure">
        <div ref={previewRef} className="ds-graphics-stage website-graphic" data-motion={inView ? 'running' : 'paused'} role="img" aria-label={specimen.alternative}><div aria-hidden="true" className="ds-graphics-art"><WebsiteGraphic key={specimen.kind} kind={specimen.kind}/></div></div>
        <figcaption><h3>{specimen.title}</h3><p>{specimen.description}</p></figcaption>
      </figure>
      <div className="ds-graphics-notes"><span className="ds-meta">PATTERN / {specimen.label.toUpperCase()}</span><dl><dt>Construction</dt><dd>{specimen.construction}</dd><dt>Motion</dt><dd>{specimen.motion}</dd><dt>Keep it honest</dt><dd>Use fictional, illustrative data in marketing. Real assessments need sources, units, and stable values; animation must never invent a result.</dd></dl><p className="ds-note">These are the same illustrations used on the homepage. Use the theme control to review their light and dark treatments.</p></div>
    </div>
  </div>;
}

const viewports = [390, 768, 1024, 1440, 1920];
const contentWidth = (width) => Math.min(siteLayout.contentMax, width - 2 * (width < siteLayout.desktopBreakpoint ? siteLayout.compactGutter : siteLayout.desktopGutter));
const previousWidth = (width) => Math.min(1344, width - (width <= 760 ? 40 : 96));
function BrandLayout() {
    const [viewport, setViewport] = useState(1440);
    const content = contentWidth(viewport);
    const margin = (viewport - content) / 2;
    return <div className="ds-layout-standard">
    <div className="ds-layout-facts"><div><strong>{siteLayout.contentMax}px</strong><span>Maximum content width</span></div><div><strong>{siteLayout.desktopGutter}px</strong><span>Minimum desktop margin</span></div><div><strong>{siteLayout.compactGutter}px</strong><span>Margin below {siteLayout.desktopBreakpoint}px</span></div></div>
    <div className="ds-layout-controls" role="group" aria-label="Layout preview screen width">{viewports.map(width => <button key={width} type="button" aria-pressed={viewport === width} onClick={() => setViewport(width)}>{width}px</button>)}</div>
    <div className="ds-layout-diagram" role="img" aria-label={`At ${viewport} pixels: ${content} pixels of content with ${margin} pixel margins on each side.`}>
      <div className="ds-layout-ruler"><span>{margin}px</span><strong>{content}px content</strong><span>{margin}px</span></div>
      <div className="ds-layout-model" style={{ paddingInline: `${margin / viewport * 100}%` }}>
        <div className="ds-layout-model-header"><b>AMLOK</b><span>Action</span></div>
        <div className="ds-layout-model-grid">{Array.from({ length: viewport < 768 ? 4 : viewport < 1024 ? 8 : 12 }, (_, index) => <i key={index}/>)}</div>
        <div className="ds-layout-model-row"><span /><span /></div>
        <div className="ds-layout-model-footer">Shared left and right edges</div>
      </div>
    </div>
    <p className="ds-note">The AMLOK content area is 1,280px wide, with 48px minimum desktop gutters. Our layout tokens express the usable width directly.</p>
    <div className="ds-spec-scroll" role="region" tabIndex={0} aria-label="Previous and standard website width comparison"><table className="ds-spec-table"><thead><tr><th>Screen width</th><th>Previous AMLOK</th><th>New shared width</th><th>Side margin</th></tr></thead><tbody>{viewports.map(width => <tr key={width}><td>{width}px</td><td>{previousWidth(width)}px</td><td>{contentWidth(width)}px</td><td>{(width - contentWidth(width)) / 2}px</td></tr>)}</tbody></table></div>
  </div>;
}

const illustrationDescriptions = {
    verification: 'An identity card is matched to a business document as a scan checks the evidence.',
    underwriting: 'Source documents converge into a credit memo with policy evidence and a human review gate.',
    monitoring: 'A square signal field scans a portfolio and isolates a borrower whose conditions have changed.',
    servicing: 'A borrower conversation connects an information request with an approved payment schedule.',
    investigation: 'Two records share a highlighted reference, revealing a connection for an investigator to review.',
    graph: 'A branching constellation connects financial entities across ownership, accounts, and transactions.',
    financial: 'Fragmented transaction records are reconciled into one structured financial record.',
    decision: 'Evidence passes through a policy gate, with an exception routed to the credit team.',
    simulation: 'A portfolio and its digital twin are compared side by side, with a changed scenario isolated in a raised cobalt plane.',
    customer: 'The institution’s customer experience sits above the connected AMLOK operating layers.',
    browser: 'A browser agent selects an application field and carries its source-linked evidence into a review.',
    embedded: 'An AMLOK intelligence module fits directly into an institution’s existing product interface.',
    workflow: 'An agent workflow branches between evidence requests and a human approval step.',
    api: 'Raw transaction strings pass through a structured API boundary and emerge as labeled data.',
    compliance: 'A policy shield checks an incoming document and identifies an exception for review.',
    quality: 'A field of interaction records is inspected, with one conversation enlarged for quality review.',
    builder: 'An operating procedure is translated into modular, connected agent instructions.',
    testing: 'Several scenario paths run through a sandbox and arrive at distinct test outcomes.',
    observability: 'A highlighted source passage is linked to the exact statement it supports.',
    support: 'An institution and an AMLOK specialist collaborate around a shared implementation plan.',
    channels: 'Voice, messaging, and a web experience converge into a single borrower conversation.',
};
function Label({ x, y, children, tone = '', size = 12 }) {
    return <text x={x} y={y} className={'pi-label ' + tone} style={{ fontSize: size }}>{children}</text>;
}
function Box({ x, y, w, h, children, tone = '' }) {
    return <g className={'pi-box ' + tone} transform={'translate(' + x + ' ' + y + ')'}><rect width={w} height={h} className={'pi-panel ' + tone}/><path d={'M1 1H' + (w - 1)} className="pi-edge-light"/>{children}</g>;
}
function Signal({ x, y, tone = '' }) {
    return <g className={'pi-signal ' + tone} transform={'translate(' + x + ' ' + y + ')'}><circle r="9" className="pi-halo"/><circle r="3.5"/></g>;
}
function Connection({ d, attention = false }) {
    return <><path d={d} className="pi-connection"/><path d={d} className={'pi-flow' + (attention ? ' secondary' : '')}/></>;
}
function Glyph({ name, x = 0, y = 0, size = 24, tone = '' }) {
    const paths = {
        person: 'M8 7a4 4 0 1 0 8 0 4 4 0 0 0-8 0ZM4 22v-4c0-5 16-5 16 0v4',
        document: 'M5 2h10l4 4v16H5ZM14 2v5h5M8 11h8M8 15h8M8 19h5',
        shield: 'M3 3h18v12l-9 7-9-7ZM8 11l3 3 6-7',
        message: 'M2 3h20v14H9l-5 4v-4H2ZM6 8h12M6 12h8',
        calendar: 'M3 4h18v18H3ZM3 9h18M7 1v6M17 1v6M7 13h3v3H7M14 13h3v3h-3',
        cursor: 'M5 2v18l5-5 4 7 4-2-4-7h7Z',
        code: 'm8 5-6 7 6 7M16 5l6 7-6 7M14 2l-4 20',
        building: 'M4 22V3h16v19M1 22h22M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2M10 22v-4h4v4',
        check: 'm5 12 5 5L20 5',
        phone: 'M6 2h12v20H6ZM6 17h12M10 20h4',
        voice: 'M10 3v12M14 3v12M6 8v6c0 8 12 8 12 0V8M12 20v3M8 23h8',
        link: 'm9 14 6-6M8 16l-2 2c-5 5-9-3-5-6l6-6c4-4 9 0 6 4M16 8l2-2c5-5 9 3 5 6l-6 6c-4 4-9 0-6-4',
        flag: 'M5 23V2M5 3h14l-4 5 4 5H5',
    };
    return <svg x={x} y={y} width={size} height={size} viewBox="0 0 24 24" className={'pi-glyph ' + tone}><path d={paths[name]}/></svg>;
}
function Caption({ children }) {
    return <g className="pi-caption"><path d="M24 22h9" className="pi-outline"/><Label x={42} y={26} tone="telemetry muted" size={8}>{children}</Label></g>;
}
function Paper({ x, y, w = 150, h = 186, title, children, tone = '' }) {
    return <g className={'pi-paper ' + tone} transform={'translate(' + x + ' ' + y + ')'}><path d={'M0 0H' + (w - 22) + 'L' + w + ' 22V' + h + 'H0Z'} className={'pi-panel ' + tone}/><path d={'M1 1H' + (w - 23)} className="pi-edge-light"/><path d={'M' + (w - 22) + ' 0V22H' + w} className="pi-fold"/>{title && <Label x={16} y={35} size={11} tone="strong">{title}</Label>}{children}</g>;
}
/* Material is shared; composition and focal objects remain specific to each story. */
function IllustrationMaterials({ id }) {
    return <defs>
    <linearGradient id={id + '-ceramic'} x1="0" y1="0" x2="1" y2="1"><stop className="pi-stop-canvas"/><stop offset="1" className="pi-stop-ceramic"/></linearGradient>
    <linearGradient id={id + '-cobalt'} x1="0" y1="0" x2="1" y2="1"><stop className="pi-stop-signal"/><stop offset=".55" className="pi-stop-cobalt"/><stop offset="1" className="pi-stop-identity"/></linearGradient>
    <radialGradient id={id + '-hero'} cx="0" cy="0" r="1" gradientTransform={heroGradient.svgTransform}>{heroGradient.stops.map(stop => <stop key={stop.offset} offset={stop.offset} stopColor={stop.color}/>)}</radialGradient>
    <linearGradient id={id + '-soft'} x1="0" y1="0" x2="1" y2="1"><stop className="pi-stop-canvas"/><stop offset="1" className="pi-stop-blue-soft"/></linearGradient>
    <linearGradient id={id + '-scan'}><stop stopColor="var(--blue-secondary)" stopOpacity="0"/><stop offset=".5" stopColor="var(--blue-secondary)" stopOpacity=".2"/><stop offset="1" stopColor="var(--blue-secondary)" stopOpacity="0"/></linearGradient>
    <filter id={id + '-shadow'} x="-35%" y="-35%" width="180%" height="190%" colorInterpolationFilters="sRGB"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="var(--identity-blue)" floodOpacity=".06"/><feDropShadow dx="0" dy="12" stdDeviation="11" floodColor="var(--identity-blue)" floodOpacity=".10"/></filter>
  </defs>;
}
function BrandCore({ x, y, size = 52 }) {
    return <g transform={'translate(' + x + ' ' + y + ')'} className="pi-core"><path d={'M0 0H' + size + 'V' + size + 'H0Z'} className="pi-blue-block pi-elevated"/><path d={'M0 ' + size + 'l8 5h' + size + 'v-' + size + 'l-8-5v' + size + 'Z'} className="pi-side-face"/><svg x={size * .18} y={size * .18} width={size * .64} height={size * .64} viewBox="0 0 32 32"><path d="M3 26 13 6h6l10 20h-7L16 13l-3.5 7H19l3 6H3Z" fill="var(--on-brand)"/></svg><path d={'M1 1H' + (size - 1)} className="pi-edge-light"/></g>;
}
function Badge({ x, y, label, tone = 'blue', icon = 'check', w = 124 }) {
    return <Box x={x} y={y} w={w} h={31} tone={tone === 'blue' ? 'selected' : tone === 'warning' ? 'attention' : ''}><Glyph name={icon} x={10} y={8} size={15} tone={tone === 'warning' ? 'attention' : 'blue'}/><Label x={33} y={20} size={9} tone={tone === 'warning' ? 'warning' : 'blue'}>{label}</Label></Box>;
}
function RadarField({ x = 0, y = 0, size = 208 }) {
    return <g transform={'translate(' + x + ' ' + y + ') scale(' + size / 208 + ')'} className="pi-radar-field"><rect width="208" height="208" className="pi-blue-block pi-elevated"/>{Array.from({ length: 9 }, (_, i) => <path key={i} d={'M' + i * 26 + ' 0V208M0 ' + i * 26 + 'H208'} className="pi-inverse-grid"/>)}{[32, 60, 88].map(n => <rect key={n} x={104 - n} y={104 - n} width={n * 2} height={n * 2} className="pi-radar-contour"/>)}<path d="M0 208 104 0 208 208M42 124H166" className="pi-radar-diagonal"/>{[[35, 52], [78, 144], [144, 72], [175, 156], [113, 106]].map(([a, b], i) => <g key={i}><circle cx={a} cy={b} r={i === 4 ? 10 : 6} className="pi-radar-halo"/><circle cx={a} cy={b} r={i === 4 ? 3 : 2} className={i === 4 ? 'pi-radar-alert' : 'pi-radar-dot'}/></g>)}<g className="pi-radar-sweep"><rect x="0" y="0" width="208" height="26" className="pi-radar-band"/><path d="M0 26H208" className="pi-radar-beam"/></g><path d="M97 90h32v32H97Z" className="pi-radar-target"/></g>;
}
function DocumentLines({ x = 16, y = 54, width = 100, count = 4 }) {
    return <g>{Array.from({ length: count }, (_, i) => <path key={i} d={'M' + x + ' ' + (y + i * 15) + 'h' + (width - [0, 19, 8, 34][i % 4])} className="pi-document-line"/>)}</g>;
}
function Brackets({ x, y, w, h }) {
    return <path d={'M' + x + ' ' + (y + 12) + 'V' + y + 'h12M' + (x + w - 12) + ' ' + y + 'h12v12M' + (x + w) + ' ' + (y + h - 12) + 'v12h-12M' + (x + 12) + ' ' + (y + h) + 'H' + x + 'v-12'} className="pi-outline"/>;
}
function PortfolioField({ x = 0, y = 0, small = false, variant = false }) {
    const cell = small ? 18 : 26, gap = small ? 7 : 10;
    return <g transform={'translate(' + x + ' ' + y + ')'}>{Array.from({ length: 20 }, (_, i) => {
            const active = variant ? [3, 8, 13, 14].includes(i) : [2, 7, 11].includes(i);
            return <rect key={i} x={(i % 5) * (cell + gap)} y={Math.floor(i / 5) * (cell + gap)} width={cell} height={cell} className={active ? (variant ? 'pi-tile violet' : 'pi-tile blue') : 'pi-tile'} style={{ animationDelay: (i * 110) + 'ms' }}/>;
        })}</g>;
}
function Verification({ step }) {
    return <><Caption>VERIFY / CONNECT THE EVIDENCE</Caption>
    <g className="pi-context"><Paper x={47} y={67} w={207} h={200} title="Business registration"><Glyph name="building" x={18} y={59} size={34} tone="blue"/><DocumentLines x={69} y={68} width={107} count={3}/><path d="M18 116H185" className="pi-grid"/><Label x={18} y={140} size={11}>Example Co.</Label><Label x={18} y={161} size={9} tone="muted">Ownership · source 01</Label><DocumentLines x={18} y={181} width={117} count={1}/></Paper></g>
    <Connection d="M155 174H300V126"/>
    <g className="pi-hover-card"><Box x={160} y={75} w={285} h={144}><rect x={0} width={5} height={144} className="pi-blue-block"/><rect x={20} y={20} width={76} height={100} className="pi-blue-block"/><path d="M20 120 58 40 96 120" className="pi-facet-line"/><Glyph name="person" x={38} y={42} size={40} tone="inverse"/><Label x={113} y={35} size={9} tone="telemetry muted">APPLICANT / 024</Label><Label x={113} y={62} size={19} tone="strong">Identity resolved</Label><Label x={113} y={83} size={10} tone="muted">Connected to the business.</Label><path d="M113 98H265" className="pi-grid"/><Glyph name="check" x={113} y={108} size={17} tone="blue"/><Label x={137} y={121} size={10}>Evidence matched</Label><g className="pi-scan-id"><path d="M13 22H103" className="pi-scan-line"/></g></Box></g>
    <Badge x={278} y={238} w={166} label={['Identity match', 'Ownership linked', 'Evidence complete', 'Screening reviewed'][step % 4]}/>
  </>;
}
function Underwriting({ step }) {
    const items = ['Repayment capacity', 'Credit-policy fit', 'Unresolved risks', 'Reassessment'];
    return <><Caption>UNDERWRITE / EVIDENCE INTO JUDGMENT</Caption>
    <Paper x={30} y={82} w={175} h={176} title="Borrower evidence"><DocumentLines width={126} count={4}/><Glyph name="link" x={17} y={139} size={17} tone="blue"/><Label x={43} y={152} size={9} tone="muted">3 linked sources</Label></Paper>
    <path d="M192 121H260" className="pi-connection"/>
    <Box x={222} y={49} w={229} h={213}><rect width={229} height={64} className="pi-blue-block"/><Label x={18} y={23} size={9} tone="inverse telemetry">AMLOK / CREDIT MEMO</Label><Label x={18} y={48} size={20} tone="inverse">A clearer decision.</Label>{items.map((s, i) => <g key={s}><rect x={12} y={76 + i * 28} width={205} height={26} className={step === i ? 'pi-selection' : 'pi-clear'}/><Glyph name={i === 2 ? 'flag' : 'check'} x={21} y={81 + i * 28} size={15} tone={i === 2 ? 'attention' : 'blue'}/><Label x={47} y={93 + i * 28} size={11}>{s}</Label></g>)}</Box>
    <BrandCore x={171} y={131} size={48}/><Badge x={274} y={265} w={177} label="Final decision: your team" icon="person"/>
  </>;
}
function Monitoring() {
    return <><Caption>MONITOR / A SIGNAL IN THE NOISE</Caption><RadarField x={48} y={49} size={226}/>
    <Connection attention d="M171 164H307V150"/>
    <Box x={285} y={108} w={171} h={103}><Label x={16} y={24} size={8} tone="telemetry muted">BORROWER / 024</Label><Label x={16} y={50} size={17} tone="strong">Change detected.</Label><path d="M16 64H155" className="pi-grid"/><Signal x={22} y={84} tone="attention"/><Label x={38} y={88} size={10} tone="warning">Compare with baseline</Label></Box>
    <Badge x={292} y={228} w={151} label="Evidence attached" icon="link"/>
  </>;
}
function Servicing({ step }) {
    return <><Caption>SERVICE / CONTEXT IN EVERY CONVERSATION</Caption>
    <Box x={58} y={57} w={285} h={185}><Label x={19} y={27} size={9} tone="telemetry muted">BORROWER CONVERSATION</Label><path d="M19 43H264" className="pi-grid"/><Glyph name="person" x={19} y={58} size={23}/><Label x={55} y={72} size={12}>Your latest documents are ready.</Label><Label x={55} y={92} size={9} tone="muted">Connected to your account</Label><DocumentLines x={55} y={126} width={166} count={2}/></Box>
    <g className="pi-hover-card"><path d="M112 169H385V230H366V246L344 230H112Z" className="pi-blue-block pi-elevated"/><Glyph name="check" x={129} y={185} size={23} tone="inverse"/><Label x={164} y={194} size={12} tone="inverse">Received. Your team has the context.</Label><Label x={164} y={214} size={9} tone="inverse muted">Ready for the next step.</Label></g>
    <Box x={321} y={53} w={126} h={103}><Label x={14} y={22} size={8} tone="telemetry blue">NEXT PAYMENT</Label><Label x={14} y={66} size={39} tone="strong">28</Label><Label x={70} y={61} size={11} tone="muted">OCT</Label><path d="M14 79H111" className="pi-grid"/><Label x={14} y={94} size={8} tone="muted">Schedule connected</Label></Box>
    <Label x={58} y={279} size={8} tone="telemetry blue">{['INFORMATION REQUEST', 'ACCOUNT CONTEXT', 'PAYMENT REMINDER', 'APPROVED REPAYMENT'][step % 4]}</Label>
  </>;
}
function Investigation({ step }) {
    return <><Caption>INVESTIGATE / SEE THE HIDDEN CONNECTION</Caption>
    <Box x={35} y={60} w={194} h={161}><Glyph name="building" x={17} y={17} size={28} tone="blue"/><Label x={59} y={30} size={12} tone="strong">Application 024</Label><Label x={59} y={47} size={8} tone="muted">Business record</Label><DocumentLines x={17} y={74} width={151} count={2}/><rect x={13} y={108} width={168} height={33} className="pi-attention-fill"/><Label x={24} y={129} size={10}>120 Example Street</Label></Box>
    <Box x={256} y={105} w={194} h={161}><rect width={194} height={5} className="pi-blue-block"/><Glyph name="person" x={17} y={20} size={26} tone="blue"/><Label x={59} y={33} size={12} tone="strong">Entity record 018</Label><Label x={59} y={50} size={8} tone="muted">Related evidence</Label><DocumentLines x={17} y={77} width={151} count={2}/><rect x={13} y={108} width={168} height={33} className="pi-attention-fill"/><Label x={24} y={129} size={10}>120 Example Street</Label></Box>
    <Connection attention d="M216 184H241V229H269"/><Signal x={241} y={205} tone="attention"/>
    <Badge x={279} y={57} w={170} label={['Shared reference', 'Context required', 'Compare evidence', 'Related entity'][step % 4]} tone="warning" icon="link"/>
  </>;
}
function RiskGraph() {
    const nodes = [[55, 83], [118, 48], [178, 85], [254, 58], [324, 82], [417, 54], [433, 154], [370, 226], [283, 262], [202, 229], [119, 256], [46, 202], [25, 142], [140, 153], [235, 145], [333, 157]];
    const edges = [[0, 1], [0, 12], [0, 13], [1, 2], [2, 3], [2, 13], [2, 14], [3, 4], [4, 5], [4, 14], [4, 15], [5, 6], [6, 7], [7, 8], [7, 15], [8, 9], [8, 14], [9, 10], [9, 13], [10, 11], [11, 12], [11, 13], [13, 14], [14, 15]];
    return <><Caption>RESEARCH / FINANCIAL RELATIONSHIPS, RESOLVED</Caption>{edges.map(([a, b], i) => <Connection key={i} d={'M' + nodes[a][0] + ' ' + nodes[a][1] + 'L' + nodes[b][0] + ' ' + nodes[b][1]}/>)}{nodes.map(([x, y], i) => <g key={i}><rect x={x - 9} y={y - 9} width={18} height={18} className={i % 3 === 0 ? 'pi-blue-block' : 'pi-panel pi-elevated'}/>{i % 3 === 0 && <circle cx={x} cy={y} r={2} className="pi-radar-dot"/>}</g>)}<Box x={169} y={115} w={153} h={65} tone="brand"><Label x={15} y={22} size={8} tone="telemetry muted">CONNECTED ENTITY</Label><Label x={15} y={48} size={20}>Puppy Store</Label></Box><Label x={29} y={63} size={8} tone="muted">Ownership</Label><Label x={351} y={100} size={8} tone="muted">Transactions</Label><Label x={61} y={284} size={8} tone="muted">Accounts</Label><Label x={353} y={252} size={8} tone="muted">Counterparties</Label></>;
}
function Financial() {
    return <><Caption>FINANCIAL INTELLIGENCE / CONNECT THE PICTURE</Caption>
    {['INTERAC E-TRF', 'STRIPE PAYOUT', 'PAD 09411'].map((a, i) => <Box key={a} x={26 + i * 12} y={65 + i * 58} w={197} h={46}><Glyph name={i === 2 ? 'building' : 'document'} x={12} y={13} size={19} tone="blue"/><Label x={42} y={20} size={8} tone="telemetry muted">{a}</Label><Label x={42} y={36} size={12}>{['+$12,480.00', '+$3,250.00', '−$1,840.00'][i]}</Label></Box>)}
    <Connection d="M232 156H279"/><BrandCore x={214} y={132} size={43}/>
    <Box x={281} y={64} w={174} h={193} tone="brand"><Label x={17} y={27} size={8} tone="telemetry">RESOLVED RECORD</Label><Label x={17} y={57} size={19}>Example Co.</Label><path d="M17 73H157" className="pi-inverse-grid"/>{[['ENTITY', 'Business identified'], ['CATEGORY', 'Operating revenue'], ['EVIDENCE', 'Source linked']].map(([a, b], i) => <g key={a}><Label x={17} y={94 + i * 38} tone="telemetry muted" size={7}>{a}</Label><Label x={17} y={110 + i * 38} size={11}>{b}</Label></g>)}</Box>
  </>;
}
function Decision() {
    return <><Caption>DECISION INTELLIGENCE / YOUR POLICY. YOUR CONTROL.</Caption>
    {[0, 1, 2].map(i => <Box key={i} x={28 + i * 6} y={66 + i * 56} w={106} h={40}><Glyph name={i === 0 ? 'document' : i === 1 ? 'building' : 'link'} x={12} y={11} size={19} tone="blue"/><Label x={41} y={25} size={10}>{['Evidence', 'Policy', 'Context'][i]}</Label></Box>)}
    <Connection d="M136 142H179M253 142H284V89H321M284 142V217H321"/>
    <path d="M174 62H251l18 18v148h-77l-18-18Z" className="pi-blue-block pi-elevated"/><path d="M251 62v148h-77M251 210l18 18" className="pi-facet-line"/><Glyph name="shield" x={201} y={118} size={38} tone="inverse"/>
    <Box x={315} y={62} w={140} h={61}><Glyph name="check" x={12} y={19} size={23} tone="blue"/><Label x={45} y={27} size={11}>Within criteria</Label><Label x={45} y={44} size={8} tone="muted">Policy aligned</Label></Box><Box x={315} y={185} w={140} h={66}><Glyph name="person" x={12} y={18} size={25} tone="blue"/><Label x={45} y={28} size={11}>Your team</Label><Label x={45} y={46} size={8} tone="muted">Reviews exceptions</Label></Box><Signal x={284} y={142}/>
    <Label x={173} y={273} size={8} tone="telemetry blue">POLICY ENGINE</Label>
  </>;
}
function Simulation() {
    return <><Caption>DIGITAL TWIN / TEST ANOTHER REALITY</Caption>
    <path d="M35 199H197l30 19H65ZM255 184H417l30 19H285Z" className="pi-floor-shadow"/>
    <g transform="translate(37 58)"><path d="M0 17 24 0H184V162l-24 17H0Z" className="pi-side-face"/><Box x={0} y={17} w={160} h={162}><Label x={15} y={25} size={10} tone="strong">Your portfolio</Label><g transform="translate(15 45) scale(.86)"><PortfolioField small/></g><Label x={15} y={149} size={8} tone="muted">Baseline / preserved</Label></Box><path d="M0 17 24 0H184L160 17Z" className="pi-facet-top"/></g>
    <path d="M207 151h38m-6-6 6 6-6 6" className="pi-outline"/>
    <g className="pi-twin-shift"><g transform="translate(257 43)"><path d="M0 17 24 0H184V162l-24 17H0Z" className="pi-side-face"/><Box x={0} y={17} w={160} h={162} tone="brand"><Label x={15} y={25} size={10}>Digital twin</Label><g transform="translate(15 45) scale(.86)"><PortfolioField small variant/></g><Label x={15} y={149} size={8} tone="muted">Scenario / revised policy</Label></Box><path d="M0 17 24 0H184L160 17Z" className="pi-facet-top blue"/></g></g>
    <Badge x={165} y={257} w={154} label="Original stays unchanged" icon="shield"/>
  </>;
}
function Customer() {
    return <><Caption>CUSTOMER / YOUR EXPERIENCE ON TOP</Caption>
    {[0, 1, 2].map(i => <g key={i}><path d={'M91 ' + (143 + i * 33) + 'H352L394 ' + (166 + i * 33) + 'H133Z'} className={i === 2 ? 'pi-blue-block' : 'pi-facet-top'}/><path d={'M133 ' + (166 + i * 33) + 'V' + (178 + i * 33) + 'H394V' + (166 + i * 33) + 'Z'} className={i === 2 ? 'pi-side-face' : 'pi-selection'}/><path d={'M91 ' + (143 + i * 33) + 'v12l42 23v-12Z'} className="pi-side-face"/></g>)}
    <Box x={111} y={48} w={282} h={108}><Glyph name="building" x={20} y={24} size={38} tone="blue"/><Label x={74} y={42} size={19} tone="strong">Your institution</Label><Label x={74} y={64} size={10} tone="muted">Brand · relationship · decision</Label><path d="M20 86H261" className="pi-grid"/></Box><Connection d="M86 92H57V217H91"/><Signal x={57} y={143}/><Label x={140} y={280} size={8} tone="telemetry blue">AMLOK / THE OPERATING LAYERS</Label>
  </>;
}
function Browser() {
    return <><Caption>BROWSER AGENTS / WORK WHERE YOU WORK</Caption>
    <Box x={27} y={47} w={363} h={222}><rect width={363} height={29} className="pi-chrome"/><Signal x={18} y={14}/><Label x={36} y={18} size={8} tone="telemetry muted">YOUR EXISTING SYSTEM</Label><rect x={1} y={30} width={50} height={191} className="pi-chrome"/>{['person', 'document', 'calendar'].map((n, i) => <Glyph key={n} name={n} x={16} y={52 + i * 46} size={19}/>)}<Label x={70} y={63} tone="strong" size={18}>Borrower application</Label><Label x={70} y={89} size={10} tone="muted">Financial statements</Label><Box x={69} y={104} w={273} h={42} tone="selected"><Glyph name="document" x={12} y={11} size={20} tone="blue"/><Label x={44} y={26} size={11}>Statement_2026.pdf</Label><Glyph name="check" x={241} y={13} size={18} tone="blue"/></Box><Brackets x={62} y={97} w={287} h={56}/><DocumentLines x={70} y={174} width={171} count={2}/></Box>
    <g className="pi-agent-cursor"><Glyph name="cursor" x={310} y={170} size={37} tone="blue"/></g>
    <Box x={252} y={227} w={204} h={49} tone="brand"><Signal x={20} y={24}/><Label x={38} y={22} size={12}>Evidence captured</Label><Label x={38} y={38} size={8} tone="muted">Original source stays attached</Label></Box>
  </>;
}
function Embedded() {
    return <><Caption>EMBEDDED / PART OF YOUR PRODUCT</Caption>
    <Box x={29} y={49} w={385} h={215}><rect width={385} height={30} className="pi-chrome"/><Label x={16} y={19} size={9} tone="telemetry">YOUR PRODUCT</Label><rect x={15} y={47} width={103} height={151} className="pi-chrome"/><Glyph name="person" x={49} y={64} size={33}/><Label x={27} y={124} size={10}>Borrower profile</Label><DocumentLines x={27} y={144} width={72} count={2}/><Label x={145} y={64} size={11} tone="strong">Financial context</Label><DocumentLines x={145} y={91} width={217} count={4}/></Box>
    <g className="pi-module-insert"><Box x={193} y={117} w={252} h={154} tone="brand"><Label x={18} y={25} size={8} tone="telemetry muted">AMLOK / CONNECTED INTELLIGENCE</Label><Label x={18} y={57} size={20}>The complete picture.</Label><Label x={18} y={80} size={10} tone="muted">Evidence. Context. Next steps.</Label><path d="M18 96H234" className="pi-inverse-grid"/><Glyph name="document" x={18} y={113} size={22} tone="inverse"/><Label x={52} y={124} size={11}>Borrower file connected</Label><Label x={52} y={141} size={8} tone="muted">Inside your existing workspace</Label></Box></g>
  </>;
}
function Workflow() {
    return <><Caption>WORKFLOW AGENTS / COORDINATE THE WORK</Caption>
    <Connection d="M130 151H195M259 151H290V85H335M290 151V222H335"/>
    <Box x={24} y={115} w={114} h={70}><Glyph name="document" x={15} y={17} size={25} tone="blue"/><Label x={50} y={29} size={12}>New file</Label><Label x={15} y={56} size={9} tone="muted">Evidence received</Label></Box>
    <BrandCore x={190} y={119} size={65}/><Label x={176} y={211} size={8} tone="telemetry blue">WORKFLOW AGENT</Label>
    <Box x={324} y={54} w={133} h={67}><Glyph name="check" x={13} y={14} size={20} tone="blue"/><Label x={44} y={28} size={11}>Verify evidence</Label><Label x={14} y={52} size={9} tone="muted">Source checks complete</Label></Box><Box x={324} y={187} w={133} h={68}><Glyph name="person" x={13} y={14} size={22} tone="blue"/><Label x={44} y={29} size={11}>Your team</Label><Label x={14} y={53} size={9} tone="muted">Approval before action</Label></Box>
    <Badge x={154} y={50} w={136} label="Your policy, applied" icon="shield"/>
  </>;
}
function Api() {
    return <><Caption>API / INTELLIGENCE AT THE BOUNDARY</Caption>
    {['INTERAC E-TRF ***a2', 'STRIPE MSP DEPOSIT', 'PAD SPF*94110NT'].map((s, i) => <Box key={s} x={23 + i * 9} y={73 + i * 54} w={190} h={39}><Label x={12} y={24} size={10} tone="code">{s}</Label></Box>)}
    <Connection d="M221 143H265"/>
    <Box x={255} y={54} w={202} h={215} tone="brand"><Label x={18} y={25} size={8} tone="telemetry muted">AMLOK / STRUCTURED RESPONSE</Label><path d="M18 38H184" className="pi-inverse-grid"/><Label x={18} y={64} size={18} tone="code">{'{'}</Label>{[['entity', 'example_business'], ['category', 'operating_revenue'], ['evidence', 'source_01']].map(([a, b], i) => <g key={a}><Label x={34} y={85 + i * 38} size={9} tone="code muted">{a + ':'}</Label><Label x={34} y={102 + i * 38} size={10} tone="code">{b}</Label></g>)}<Label x={18} y={205} size={18} tone="code">{'}'}</Label></Box><Glyph name="code" x={214} y={128} size={33} tone="blue"/>
  </>;
}
function Compliance() {
    return <><Caption>COMPLIANCE / POLICY THROUGHOUT THE WORK</Caption>
    <Paper x={41} y={62} w={181} h={200} title="Policy requirements"><DocumentLines width={133} count={5}/><rect x={13} y={144} width={154} height={27} className="pi-selection"/><Label x={24} y={162} size={10}>Evidence + consent</Label></Paper><Connection d="M222 157H281"/>
    <path d="M281 53H428V180L354 237 281 180Z" className="pi-blue-block pi-elevated"/><path d="M294 66H415V174L354 220 294 174Z" className="pi-facet-line"/><path d="m324 126 22 22 41-48" className="pi-shield-check"/><path d="M354 53V237" className="pi-facet-line"/>
    <Badge x={247} y={250} w={201} label="Exceptions reach your team" icon="flag" tone="warning"/>
  </>;
}
function Quality() {
    return <><Caption>QUALITY / EACH INTERACTION MATTERS</Caption>
    <g transform="translate(29 66)">{Array.from({ length: 30 }, (_, i) => <g key={i} transform={'translate(' + ((i % 6) * 33) + ' ' + (Math.floor(i / 6) * 36) + ')'}><rect width={25} height={27} className={i === 14 ? 'pi-panel attention' : i % 4 === 0 ? 'pi-blue-block' : 'pi-panel'}/><Glyph name={i === 14 ? 'flag' : 'check'} x={5} y={6} size={15} tone={i === 14 ? 'attention' : i % 4 === 0 ? 'inverse' : 'blue'}/></g>)}</g>
    <Connection d="M107 151H260V125H288"/><Brackets x={91} y={132} w={37} h={39}/>
    <Box x={274} y={68} w={180} h={188}><rect width={180} height={48} className="pi-blue-block"/><Glyph name="message" x={15} y={13} size={23} tone="inverse"/><Label x={49} y={28} size={11} tone="inverse">Interaction 014</Label><Label x={16} y={78} size={16} tone="strong">Context in focus.</Label><DocumentLines x={16} y={97} width={144} count={3}/><rect x={13} y={122} width={154} height={25} className="pi-attention-fill"/><Label x={23} y={139} size={10} tone="warning">Review this response</Label><Label x={16} y={172} size={9} tone="muted">Source evidence attached</Label></Box>
  </>;
}
function Builder() {
    return <><Caption>AGENT BUILDER / TURN PROCEDURE INTO ACTION</Caption>
    <Paper x={25} y={66} w={188} h={200} title="Your operating procedure"><Label x={16} y={69} size={11}>1. Collect the evidence.</Label><Label x={16} y={99} size={11}>2. Apply your policy.</Label><Label x={16} y={129} size={11}>3. Ask for approval.</Label><DocumentLines y={159} width={136} count={2}/></Paper><Connection d="M213 161H271"/>
    {[['Collect evidence', 'document'], ['Evaluate policy', 'shield'], ['Request approval', 'person']].map(([label, icon], i) => <g key={label} transform={'translate(' + (263 + i * 10) + ' ' + (50 + i * 70) + ')'}><path d="M0 0 12-7h155l-12 7Z" className="pi-facet-top"/><path d="M155 0 167-7v53l-12 7Z" className="pi-side-face"/><Box x={0} y={0} w={155} h={53} tone={i === 1 ? 'brand' : ''}><Glyph name={icon} x={13} y={14} size={25} tone={i === 1 ? 'inverse' : 'blue'}/><Label x={49} y={23} size={10}>{label.split(' ')[0]}</Label><Label x={49} y={39} size={10}>{label.split(' ')[1]}</Label></Box></g>)}
  </>;
}
function Testing() {
    return <><Caption>TESTING / EXPLORE THE EDGE CASES</Caption>
    <Box x={28} y={102} w={111} h={86} tone="brand"><Glyph name="document" x={17} y={17} size={28} tone="inverse"/><Label x={17} y={66} size={13}>Sample file</Label></Box><Connection d="M139 145H183V74H260M183 145H260M183 145V229H260"/>
    {['Missing evidence', 'Policy exception', 'Changed conditions'].map((s, i) => <Box key={s} x={249} y={49 + i * 78} w={201} h={58}><rect width={4} height={58} className={i === 1 ? 'pi-attention-fill' : 'pi-blue-block'}/><Glyph name={i === 1 ? 'flag' : 'check'} x={15} y={18} size={22} tone={i === 1 ? 'attention' : 'blue'}/><Label x={48} y={25} size={11}>{s}</Label><Label x={48} y={43} size={8} tone="muted">{i === 1 ? 'Escalation expected' : 'Expected behavior checked'}</Label></Box>)}
    <Label x={28} y={264} size={8} tone="telemetry blue">SANDBOX / BEFORE DEPLOYMENT</Label>
  </>;
}
function Observability() {
    return <><Caption>OBSERVABILITY / FOLLOW IT TO THE SOURCE</Caption>
    <Paper x={40} y={52} w={210} h={224} title="Source document"><DocumentLines width={166} count={3}/><rect x={13} y={105} width={183} height={46} className="pi-blue-block"/><Label x={23} y={124} size={10} tone="inverse">Cash receipts reconciled</Label><Label x={23} y={141} size={10} tone="inverse">with the source records.</Label><DocumentLines y={177} width={166} count={2}/><Label x={167} y={213} size={8} tone="telemetry muted">P.04</Label></Paper><Connection d="M237 182H278V143H299"/>
    <Box x={277} y={91} w={179} h={123}><Label x={16} y={25} size={8} tone="telemetry blue">ASSESSMENT EXCERPT</Label><Label x={16} y={53} size={15} tone="strong">Income evidence</Label><Label x={16} y={74} size={15} tone="strong">is source-linked.</Label><Glyph name="link" x={16} y={91} size={16} tone="blue"/><Label x={40} y={104} size={9} tone="blue">[1] Source · page 4</Label></Box>
    <path d="M365 214V238" className="pi-connection"/><Label x={292} y={259} size={9} tone="muted">The evidence stays connected.</Label>
  </>;
}
function Support() {
    return <><Caption>SUPPORT / A SHARED PATH FORWARD</Caption>
    <Box x={115} y={47} w={263} h={213}><Label x={18} y={29} size={10} tone="telemetry blue">IMPLEMENTATION PLAN</Label><path d="M18 43H244" className="pi-grid"/>{['Connect the workspace', 'Configure your policies', 'Review the first workflow'].map((s, i) => <g key={s}><Glyph name={i === 2 ? 'document' : 'check'} x={18} y={65 + i * 42} size={20} tone="blue"/><Label x={49} y={79 + i * 42} size={11}>{s}</Label></g>)}</Box>
    <Box x={28} y={100} w={129} h={75}><Glyph name="person" x={15} y={14} size={25} tone="blue"/><Label x={15} y={58} size={11}>Your team</Label></Box>
    <Box x={312} y={182} w={139} h={81} tone="brand"><Glyph name="message" x={16} y={15} size={26} tone="inverse"/><Label x={16} y={62} size={12}>AMLOK specialist</Label></Box>
  </>;
}
function Channels() {
    return <><Caption>OMNICHANNEL / ONE BORROWER. EVERY CHANNEL.</Caption>
    <Box x={28} y={65} w={111} h={161}><rect x={10} y={21} width={91} height={117} className="pi-chrome"/><Glyph name="phone" x={39} y={45} size={37} tone="blue"/><Label x={22} y={112} size={11}>Your product</Label></Box>
    <Box x={179} y={45} w={111} h={72}><Glyph name="message" x={14} y={16} size={25} tone="blue"/><Label x={47} y={34} size={10}>Messaging</Label><DocumentLines x={14} y={55} width={80} count={1}/></Box>
    <Box x={179} y={187} w={111} h={72}><Glyph name="voice" x={14} y={16} size={25} tone="blue"/><Label x={47} y={35} size={11}>Voice</Label>{[10, 16, 23, 15, 10].map((h, i) => <path key={i} d={'M' + (50 + i * 7) + ' ' + (64 - h) + 'v' + h} className="pi-voice-line"/>)}</Box>
    <Connection d="M139 145H324M290 81H324V145M290 223H324V145H356"/>
    <Box x={353} y={100} w={105} h={108} tone="brand"><Glyph name="person" x={36} y={16} size={31} tone="inverse"/><Label x={12} y={68} size={11}>One borrower</Label><Label x={12} y={88} size={9} tone="muted">Shared context</Label></Box><Signal x={324} y={145}/>
  </>;
}
function Scene({ kind, step }) {
    switch (kind) {
        case 'verification': return <Verification step={step}/>;
        case 'underwriting': return <Underwriting step={step}/>;
        case 'monitoring': return <Monitoring />;
        case 'servicing': return <Servicing step={step}/>;
        case 'investigation': return <Investigation step={step}/>;
        case 'graph': return <RiskGraph />;
        case 'financial': return <Financial />;
        case 'decision': return <Decision />;
        case 'simulation': return <Simulation />;
        case 'customer': return <Customer />;
        case 'browser': return <Browser />;
        case 'embedded': return <Embedded />;
        case 'workflow': return <Workflow />;
        case 'api': return <Api />;
        case 'compliance': return <Compliance />;
        case 'quality': return <Quality />;
        case 'builder': return <Builder />;
        case 'testing': return <Testing />;
        case 'observability': return <Observability />;
        case 'support': return <Support />;
        case 'channels': return <Channels />;
    }
}
/* Small cards are composed independently: no miniature dashboard or scaled-down chart. */
function CompactScene({ kind }) {
    if (kind === 'financial')
        return <>
    {[0, 1, 2].map(i => <Box key={i} x={18 + i * 7} y={30 + i * 48} w={154} h={38}><Glyph name="document" x={11} y={11} size={17} tone="blue"/><Label x={37} y={23} size={9} tone="code">{['ETRF ***a2', 'STRIPE MSP', 'PAD 09411'][i]}</Label></Box>)}
    <Box x={166} y={58} w={134} h={112} tone="brand"><Glyph name="link" x={15} y={15} size={24} tone="inverse"/><Label x={15} y={62} size={14}>One clear record.</Label><Label x={15} y={83} size={9} tone="muted">Entity + transaction</Label><Label x={15} y={100} size={9} tone="muted">+ source evidence</Label></Box>
  </>;
    if (kind === 'decision')
        return <>
    <Connection d="M59 61H115M59 103H115M59 145H115M166 103H207V63H244M207 103V148H244"/>{[61, 103, 145].map((y, i) => <Box key={y} x={24} y={y - 16} w={42} h={33}><Glyph name={i === 1 ? 'building' : 'document'} x={11} y={7} size={21} tone="blue"/></Box>)}
    <path d="M116 29H163l13 13v131h-47l-13-13Z" className="pi-blue-block pi-elevated"/><path d="M163 29v131h-47M163 160l13 13" className="pi-facet-line"/><Glyph name="shield" x={131} y={89} size={28} tone="inverse"/>
    <Box x={238} y={38} w={61} h={48}><Glyph name="check" x={18} y={12} size={25} tone="blue"/></Box><Box x={238} y={124} w={61} h={48}><Glyph name="person" x={18} y={11} size={25} tone="blue"/></Box><Signal x={207} y={103}/><Label x={91} y={197} size={8} tone="telemetry">YOUR POLICY. YOUR DECISION.</Label>
  </>;
    if (kind === 'simulation')
        return <>
    <g transform="translate(18 43)"><path d="M0 0 16-9h118l-16 9Z" className="pi-facet-top"/><path d="M118 0 134-9v128l-16 9Z" className="pi-side-face"/><Box x={0} y={0} w={118} h={128}><Label x={12} y={23} size={12} tone="strong">Portfolio</Label><g transform="translate(12 42) scale(.65)"><PortfolioField small/></g></Box></g>
    <g className="pi-twin-shift"><g transform="translate(173 29)"><path d="M0 0 16-9h118l-16 9Z" className="pi-facet-top blue"/><path d="M118 0 134-9v128l-16 9Z" className="pi-side-face"/><Box x={0} y={0} w={118} h={128} tone="brand"><Label x={12} y={23} size={12}>Digital twin</Label><g transform="translate(12 42) scale(.65)"><PortfolioField small variant/></g></Box></g></g>
    <path d="M149 106h17m-5-5 5 5-5 5" className="pi-outline"/><Label x={75} y={197} size={8} tone="telemetry muted">EXPLORE. COMPARE. DECIDE.</Label>
  </>;
    return <><RadarField x={25} y={20} size={166}/><Connection attention d="M115 105H223V118"/><Box x={169} y={113} w={134} h={68}><Signal x={18} y={19} tone="attention"/><Label x={14} y={43} size={13} tone="strong">Change detected.</Label><Label x={14} y={59} size={8} tone="muted">Bring the context into review.</Label></Box></>;
}
function PortraitScene({ kind }) {
    if (kind === 'monitoring')
        return <><Label x={21} y={25} size={8} tone="telemetry blue">PORTFOLIO / LIVE SIGNALS</Label><RadarField x={32} y={49} size={256}/><Box x={18} y={244} w={277} h={99}><Label x={17} y={25} size={8} tone="telemetry muted">BORROWER 024 / EVIDENCE ATTACHED</Label><Label x={17} y={53} size={20} tone="strong">A change worth reviewing.</Label><Signal x={23} y={77} tone="attention"/><Label x={40} y={81} size={11} tone="warning">New conditions. Original context.</Label></Box><Badge x={66} y={361} w={230} label="Review against the original assessment" icon="link"/></>;
    return <><Label x={21} y={25} size={8} tone="telemetry blue">DEAL / EVIDENCE INTO ASSESSMENT</Label><Box x={37} y={71} w={247} h={280} tone="selected"/><Box x={21} y={51} w={247} h={280}><rect width={247} height={88} className="pi-blue-block"/><Label x={18} y={27} size={8} tone="telemetry inverse">AMLOK / CREDIT MEMO</Label><Label x={18} y={58} size={25} tone="inverse">Coffee &amp; Co</Label><Label x={18} y={76} size={9} tone="inverse muted">Prepared from linked borrower evidence</Label>{['Repayment capacity', 'Policy alignment', 'Unresolved questions'].map((label, i) => <g key={label}><path d={'M17 ' + (103 + i * 43) + 'H229'} className="pi-grid"/><Glyph name={i === 2 ? 'flag' : 'check'} x={18} y={117 + i * 43} size={19} tone={i === 2 ? 'attention' : 'blue'}/><Label x={49} y={131 + i * 43} size={12}>{label}</Label></g>)}<rect x={15} y={240} width={217} height={25} className="pi-selection"/><Label x={27} y={257} size={10} tone="blue">Final decision: your team</Label></Box><Badge x={62} y={367} w={236} label="Sources stay with the assessment" icon="link"/></>;
}
function DetailScene({ kind }) {
    if (kind === 'customer')
        return <Customer />;
    if (kind === 'verification')
        return <><Caption>ONBOARDING / THE IDENTITY COMES TOGETHER</Caption>
    {['Applicant', 'Business', 'Ownership'].map((name, i) => <g key={name} transform={'translate(' + (30 + i * 147) + ' ' + (75 + (i === 1 ? -24 : 0)) + ')'}><Box x={0} y={0} w={124} h={161} tone={i === 1 ? 'brand' : ''}><Glyph name={i === 0 ? 'person' : i === 1 ? 'building' : 'link'} x={39} y={26} size={46} tone={i === 1 ? 'inverse' : 'blue'}/><Label x={16} y={105} size={15}>{name}</Label><path d="M16 122H108" className={i === 1 ? 'pi-inverse-grid' : 'pi-grid'}/><Label x={16} y={144} size={9} tone="muted">Evidence connected</Label></Box></g>)}<Connection d="M92 236V267H386V236M240 212V267"/><Signal x={240} y={267}/>
  </>;
    if (kind === 'underwriting')
        return <><Caption>UNDERWRITING / ASSESS THE WHOLE FILE</Caption><path d="M31 92H157l17 18h274v153H31Z" className="pi-selection"/><Paper x={54} y={57} w={168} h={179} title="Capacity"><DocumentLines width={120} count={5}/></Paper><Paper x={247} y={43} w={168} h={179} title="Policy fit"><DocumentLines width={120} count={5}/></Paper><Box x={102} y={181} w={273} h={69} tone="brand"><Glyph name="person" x={19} y={20} size={30} tone="inverse"/><Label x={65} y={29} size={14} tone="inverse">Your team owns the judgment.</Label><Label x={65} y={49} size={10} tone="inverse">Evidence prepared. Questions surfaced.</Label></Box></>;
    if (kind === 'monitoring')
        return <><Caption>MONITORING / EVERY CHANGE HAS CONTEXT</Caption>
    <path d="M50 154H424" className="pi-connection"/>{[73, 181, 289, 407].map((x, i) => <g key={x}><rect x={x - 7} y={147} width={14} height={14} className={i === 3 ? 'pi-attention-fill' : 'pi-blue-block'}/><Label x={x - 24} y={184} size={8} tone="telemetry muted">{['FUNDED', 'MONTH 01', 'MONTH 02', 'TODAY'][i]}</Label></g>)}
    <Box x={28} y={47} w={178} h={77} tone="brand"><Label x={16} y={30} size={16}>Original assessment</Label><Label x={16} y={53} size={10} tone="muted">The baseline stays attached.</Label></Box><Connection d="M73 124V147"/>
    <Box x={258} y={211} w={198} h={64}><Signal x={21} y={28} tone="attention"/><Label x={43} y={28} size={14} tone="strong">New evidence arrived.</Label><Label x={43} y={49} size={9} tone="muted">Compare. Reassess. Respond.</Label></Box><Connection attention d="M407 161V211"/>
  </>;
    if (kind === 'servicing')
        return <><Caption>SERVICING / CONTEXT FOLLOWS THE CUSTOMER</Caption>
    <Box x={146} y={42} w={195} h={233}><rect width={195} height={40} className="pi-blue-block"/><Glyph name="person" x={13} y={11} size={20} tone="inverse"/><Label x={43} y={25} size={11} tone="inverse">Your institution</Label><path d="M15 59H161V105H37l-11 9v-9H15Z" className="pi-chrome"/><Label x={27} y={79} size={11}>Can you confirm</Label><Label x={27} y={96} size={11}>my next payment?</Label><path d="M36 131H182V185H166v11l-13-11H36Z" className="pi-blue-block"/><Label x={49} y={152} size={10} tone="inverse">Your account context</Label><Label x={49} y={171} size={10} tone="inverse">is already connected.</Label><path d="M79 220h37" className="pi-document-line"/></Box>
    <Box x={30} y={170} w={146} h={79}><Glyph name="calendar" x={13} y={19} size={30} tone="blue"/><Label x={53} y={33} size={12}>Next payment</Label><Label x={53} y={53} size={9} tone="muted">Schedule attached</Label></Box><Signal x={360} y={118}/><Label x={374} y={122} size={8} tone="blue">CONNECTED</Label>
  </>;
    return <><Caption>INVESTIGATION / CONNECT WHAT WAS SEPARATE</Caption>
    <Box x={30} y={55} w={184} h={134}><rect width={184} height={38} className="pi-blue-block"/><Label x={16} y={25} size={13} tone="inverse">Borrower record</Label><Label x={16} y={62} size={10} tone="muted">Associated account</Label><rect x={13} y={81} width={158} height={31} className="pi-attention-fill"/><Label x={24} y={102} size={12} tone="code">ACCT •••• 0142</Label></Box>
    <Box x={272} y={117} w={184} h={134}><Label x={16} y={29} size={16} tone="strong">Connected entity</Label><Label x={16} y={62} size={10} tone="muted">Associated account</Label><rect x={13} y={81} width={158} height={31} className="pi-attention-fill"/><Label x={24} y={102} size={12} tone="code">ACCT •••• 0142</Label></Box><Connection attention d="M214 152H243V214H272"/><Signal x={243} y={181} tone="attention"/><Label x={67} y={283} size={9} tone="muted">Shared evidence. A connection worth investigating.</Label>
  </>;
}
function ProductIllustration({ kind, step = 0, className = '', format = 'standard', brandFill = 'cobalt' }) {
    const id = 'pi-' + useId().replace(/[^a-zA-Z0-9_-]/g, '');
    const materials = { '--pi-ceramic': `url(#${id}-ceramic)`, '--pi-cobalt': `url(#${id}-${brandFill})`, '--pi-soft': `url(#${id}-soft)`, '--pi-scan': `url(#${id}-scan)`, '--pi-shadow': `url(#${id}-shadow)` };
    const ref = useRef(null);
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        const node = ref.current;
        if (!node)
            return;
        const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), { threshold: .05 });
        observer.observe(node);
        return () => observer.disconnect();
    }, []);
    return <div ref={ref} style={materials} className={'product-illustration ' + className} data-illustration={kind} data-format={format} data-brand-fill={brandFill} data-motion={visible ? 'running' : 'paused'} role="img" aria-label={'Illustrative graphic: ' + illustrationDescriptions[kind]}>
    <svg viewBox={format === 'portrait' ? '0 0 320 414' : format === 'compact' ? '0 0 320 206' : '0 0 480 300'} fill="none" aria-hidden="true" focusable="false"><IllustrationMaterials id={id}/>{format === 'portrait' ? <PortraitScene kind={kind}/> : format === 'compact' ? <CompactScene kind={kind}/> : format === 'detail' ? <DetailScene kind={kind}/> : <Scene kind={kind} step={step}/>}</svg>
  </div>;
}
function ProductIllustrationLibrary() {
    const [kind, setKind] = useState('verification');
    return <div className="ds-product-graphics"><span className="ds-meta">PRODUCT &amp; WORKFLOW GRAPHICS / LIVE REFERENCE</span><div className="ds-illustration-families">{['verification', 'monitoring', 'simulation', 'servicing', 'embedded', 'observability'].map(item => <button key={item} type="button" onClick={() => setKind(item)} aria-pressed={kind === item}><ProductIllustration kind={item}/><span>{item.charAt(0).toUpperCase() + item.slice(1)}</span></button>)}</div><label htmlFor="product-graphic-example">Choose a homepage illustration</label><select id="product-graphic-example" value={kind} onChange={event => setKind(event.target.value)}>{Object.keys(illustrationDescriptions).map(key => <option key={key} value={key}>{key.charAt(0).toUpperCase() + key.slice(1)}</option>)}</select><div className="ds-illustration-selected"><ProductIllustration kind={kind}/></div><p className="ds-note">{illustrationDescriptions[kind]} Shared colors and geometry create consistency; the subject determines the composition. Documents, scans, conversations, modular systems, and source connections each tell a different story. All sample data is fictional.</p></div>;
}

const navigation = [
    { label: 'SYSTEM', items: [['overview', 'Overview'], ['identity', 'Identity'], ['geometry', 'Geometry']] },
    { label: 'FOUNDATIONS', items: [['surfaces', 'Borders & elevation'], ['color', 'Color & themes'], ['typography', 'Typography'], ['layout', 'Layout & spacing'], ['imagery', 'Fields & imagery'], ['exploration', 'Signals & icons'], ['website-graphics', 'Website graphics']] },
    { label: 'EXPERIENCE', items: [['components', 'Controls & forms'], ['data', 'Data & workflows'], ['ai', 'AI & human decisions'], ['marketing', 'Web & marketing'], ['voice', 'Voice & content']] },
    { label: 'DELIVERY', items: [['motion', 'Motion'], ['accessibility', 'Accessibility'], ['implementation', 'Tokens & governance']] },
];
function Section({ id, number, title, description, children }) {
    return <section id={id} className="ds-section"><header className="ds-section-heading"><span className="ds-meta"><i />{number} / AMLOK DESIGN SYSTEM</span><h2>{title}</h2><p>{description}</p></header>{children}</section>;
}
function Rules({ items }) {
    return <div className="ds-rules">{items.map(([title, body], i) => <article key={title}><span className="ds-meta">{String(i + 1).padStart(2, '0')}</span><h3>{title}</h3><p>{body}</p></article>)}</div>;
}
function Specs({ headings, rows }) {
    return <div className="ds-spec-scroll" role="region" tabIndex={0} aria-label={headings.join(', ')}><table className="ds-spec-table"><thead><tr>{headings.map(h => <th key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>;
}
function BrandSystem() {
    const [active, setActive] = useState('overview');
    const [dark, setDark] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const [notice, setNotice] = useState('');
    const [paused, setPaused] = useState(true);
    const dialogRef = useRef(null);
    const toastTimer = useRef(null);
    useEffect(() => {
        const sections = Array.from(document.querySelectorAll('.ds-main>section[id]'));
        let frame = 0;
        const update = () => { frame = 0; setActive(sections.reduce((current, section) => section.getBoundingClientRect().top <= 200 ? section.id : current, 'overview')); };
        const onScroll = () => { if (!frame)
            frame = requestAnimationFrame(update); };
        update();
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => { window.removeEventListener('scroll', onScroll); cancelAnimationFrame(frame); if (toastTimer.current)
            clearTimeout(toastTimer.current); };
    }, []);
    const notify = (message) => { setNotice(message); if (toastTimer.current)
        clearTimeout(toastTimer.current); toastTimer.current = setTimeout(() => setNotice(''), 5000); };
    const copy = async (value, label) => { try {
        await navigator.clipboard.writeText(value);
        notify(`${label} copied`);
    }
    catch {
        notify('Clipboard unavailable. Download the tokens instead.');
    } };
    return <div className="ds-system amlok-brand not-prose" data-amlok-theme={dark ? 'dark' : 'light'}>
    <a href="#ds-main" className="ds-skip">Skip to guidelines</a>
    <header className="ds-topbar"><a href="/resources/brand" aria-label="AMLOK design system"><Wordmark /></a><span className="ds-topbar-title">Design system <small>v{brand.version}</small></span><div className="ds-topbar-actions"><a href="/resources/brand#implementation" className="ds-topbar-site">Design tokens <ArrowRight size={16}/></a><button className="ds-icon-button" onClick={() => setDark(!dark)} aria-label={dark ? 'Switch to light theme' : 'Switch to dark theme'}>{dark ? <Sun size={19}/> : <Moon size={19}/>}</button><button className="ds-icon-button ds-menu-toggle" aria-label="Toggle guidelines navigation" aria-expanded={menuOpen} aria-controls="ds-navigation" onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X size={20}/> : <Menu size={20}/>}</button></div></header>
    <aside className={`ds-sidebar ${menuOpen ? 'is-open' : ''}`} id="ds-navigation"><nav aria-label="Design system sections">{navigation.map(group => <div key={group.label}><p className="ds-meta">{group.label}</p>{group.items.map(([id, label]) => <a key={id} href={`#${id}`} aria-current={active === id ? 'location' : undefined} onClick={() => { setActive(id); setMenuOpen(false); }}>{label}</a>)}</div>)}</nav><a className="ds-download" href="/brand/amlok-tokens.txt" download="amlok-tokens.css"><Download size={16}/>Download tokens</a></aside>
    <main id="ds-main" className="ds-main">
      <section id="overview" className="ds-overview"><div className="ds-overview-copy"><span className="ds-meta"><i />AMLOK / SYSTEM 02</span><h1>Intelligence<br />in focus.</h1><p className="ds-overview-manifesto">Clear by design.<br />Connected by signals.</p><p>A clear, approachable system for financial risk intelligence. Rounded surfaces give content room to breathe. Precise graphics explain the work. AMLOK blue and purposeful signals connect every experience.</p><a href="#geometry" className="ds-button">Explore the system <ArrowRight size={18}/></a></div><RadarVisual paused label="STRUCTURE / SIGNAL / HUMAN CONTROL"/><div className="ds-overview-foot"><span>WEB · MARKETING · PRODUCT</span><span>INTER / JETBRAINS MONO</span><span>VERSION {brand.version} / {brand.reviewed}</span></div></section>
      <div className="ds-principles"><article><span>01 / STRUCTURE</span><p>Soft edges. Precise alignment.</p></article><article><span>02 / SIGNAL</span><p>Attention has a purpose.</p></article><article><span>03 / CONTROL</span><p>People own the decision.</p></article></div>

      <Section id="identity" number="01" title="A recognizable identity." description="The AMLOK A is the primary mark. Its straight edges and internal negative space anchor our illustrations. Rounded interface surfaces complement the mark while preserving its original geometry.">
        <div className="ds-logo-grid"><div className="ds-logo-stage"><img className="ds-logo-asset" src="/brand/amlok-logo-blue.svg" width="159" height="30" alt="AMLOK icon and wordmark in blue"/><span>FULL LOGO / LIGHT SURFACES</span></div><div className="ds-logo-stage ds-logo-inverse"><img className="ds-logo-asset" src="/brand/amlok-logo-white.svg" width="159" height="30" alt="AMLOK icon and wordmark in white"/><span>FULL LOGO / DARK SURFACES</span></div><div className="ds-symbol-stage"><Mark /><span>SYMBOL / ORIGINAL GEOMETRY</span></div></div>
        <div className="ds-asset-downloads"><a className="ds-button ds-button-secondary" href="/brand/amlok-logo-blue.svg" download><Download size={16}/>Blue full logo · SVG</a><a className="ds-button ds-button-secondary" href="/brand/amlok-logo-white.svg" download><Download size={16}/>White full logo · SVG</a><span className="ds-note">Icon + wordmark · transparent background · outlined lettering</span></div>
        <div className="ds-asset-downloads"><a className="ds-button ds-button-secondary" href="/brand/amlok-mark-blue.svg" download><Download size={16}/>Blue mark · SVG</a><a className="ds-button ds-button-secondary" href="/brand/amlok-mark-white.svg" download><Download size={16}/>White mark · SVG</a><span className="ds-note">Symbol only · for favicons and compact spaces</span></div>
        <div className="ds-profile-logo" id="profile-logo">
          <img src="/brand/amlok-profile-blue.svg" width="1024" height="1024" alt="White AMLOK symbol centered on an AMLOK blue square"/>
          <div><span className="ds-meta">SOCIAL / PROFILE LOGO</span><h3>White on AMLOK blue.</h3><p>The default profile logo for social channels and company accounts. Use the solid <strong>#052698</strong> background and the original white symbol. The square asset includes safe space for platforms that crop profile pictures into circles.</p><div className="ds-asset-downloads"><a className="ds-button" href="/brand/amlok-profile-blue.png" download><Download size={16}/>Profile logo · PNG</a><a className="ds-button ds-button-secondary" href="/brand/amlok-profile-blue.svg" download><Download size={16}/>Profile logo · SVG</a></div><p className="ds-note">1024 × 1024px PNG · Scalable SVG · Keep the supplied padding</p></div>
        </div>
        <Rules items={[["Protect the mark", "Keep one symbol-width of clear space around the logo. Use the supplied SVG. Minimum symbol size: 24px; minimum wordmark width: 112px. Use the symbol alone in compact navigation."], ["One identity, two signatures", "AMLOK is the written name. The established lowercase wordmark is the visual signature. Use blue on light surfaces and white on dark fields. Never stretch, outline, crop, rotate, or add glow to the mark."], ["Shield as a supporting motif", "Use an angular shield in illustrations and protection-related signals. It is not a replacement logo or an unearned security certification."]]}/>
      </Section>

      <Section id="geometry" number="02" title="Rounded surfaces. Precise graphics." description="A softer frame for the same intelligence. Use generous card corners, pill-shaped marketing actions, and a compact radius for working controls. Keep the logo, diagrams, and illustration geometry intact.">
        <div className="ds-radius-board">
          <article><span className="ds-meta">10 PX / WORKING CONTROLS</span><div className="ds-radius-control"><FileText size={18}/><span>Review evidence</span><ArrowRight size={16}/></div><p>Inputs and product actions stay compact and easy to align.</p></article>
          <article><span className="ds-meta">20 PX / CONTENT CARDS</span><div className="ds-radius-card"><span className="ds-meta"><i />CONNECTED EVIDENCE</span><strong>A clearer picture.</strong><span>One calm surface for related information.</span></div><p>Cards and media share a generous, consistent corner.</p></article>
          <article><span className="ds-meta">PILL / MARKETING ACTIONS</span><a className="ds-button ds-button-pill" href="/overview/introduction">Explore the platform <ArrowRight size={16}/></a><div className="ds-radius-chip"><Check size={14}/>Evidence connected</div><p>Primary calls to action and category filters feel approachable.</p></article>
        </div>
        <Specs headings={['Element', 'Radius / token', 'Usage']} rows={[["Checkboxes / keycaps", "4px / --radius-xs", "Small rectangles retain a clear selection shape."], ["Navigation items / compact badges", "8px / --radius-sm", "Use subtle rounding within dense interfaces."], ["Inputs / product buttons", "10px / --radius-control", "44px minimum preferred target height; persistent labels."], ["Nested cards / selected rows", "12px / --radius-inner", "A smaller corner inside a larger parent."], ["Menus / popovers / toasts", "16px / --radius-overlay", "A distinct floating surface with room for focus outlines."], ["Marketing cards / photography", "20px / --radius-card, --radius-media", "Clip only the media surface, never an interactive parent’s focus ring."], ["Major panels / dialogs / hero video", "24px / --radius-panel", "Use for large standalone surfaces, not every nested item."], ["Marketing CTAs / category filters", "999px / --radius-pill", "Pill actions; circular 44px icon controls. Text links stay unboxed."], ["Logo / diagrams / illustration objects", "Original geometry", "Preserve angular planes, chart bars, signal fields, and photo overlays. Round only the outer presentation frame."], ["Profile assets", "Original artwork", "Preserve the supplied assets and their safe area."]]}/>
        <Rules items={[["A rounded frame, an exact composition", "AMLOK combines open layouts and rounded calls to action with quiet surfaces, fine edges, and restrained depth. Our blue, Inter typography, hero field, and original graphics define the system."], ["Nest deliberately", "Pair a 20–24px outer card with 12px inner surfaces and 24–32px content padding. For flush media, inherit the outer corner. Avoid repeating a full-size radius on every nested element."], ["Keep function recognizable", "Circles suit icon actions, radio controls, switch thumbs, and signals. Pills suit marketing actions and filters. Reading panels and form fields remain rounded rectangles."]]}/>
      </Section>

      <Section id="surfaces" number="03" title="Quiet edges. Measured depth." description="White and soft gray do most of the work. A fine edge separates a card; a diffuse shadow indicates elevation. Keep the interface calm so the content and graphics carry the story.">
        <div className="ds-elevation-board">
          <article className="ds-elevation-flat"><span className="ds-meta">01 / RESTING</span><h3>Content surface</h3><p>A subtle 1px edge. No shadow on every card.</p><code>--border-subtle</code></article>
          <article className="ds-elevation-raised"><span className="ds-meta">02 / RAISED</span><h3>Focused content</h3><p>An inset edge and a soft, low-opacity lift.</p><code>--edge-inset + --shadow-raised</code></article>
          <article className="ds-elevation-overlay"><span className="ds-meta">03 / OVERLAY</span><h3>A layer above</h3><p>More separation for a menu or dialog.</p><code>--edge-inset + --shadow-overlay</code></article>
        </div>
        <Specs headings={['Treatment', 'Rule', 'Application']} rows={[["Resting structure", "1px subtle edge or surface contrast", "Cards, separators, and reading panels. Use --border-subtle or --border-default."], ["Interactive boundaries", "Visible control outline and selected state", "Form fields use --line-strong; selected controls use blue plus text or icon. Decorative hairlines never identify an input alone."], ["Raised surface", "Inset translucent ring + diffuse shadow", "Use --edge-inset with --shadow-raised; avoid stacking an opaque border with a heavy shadow."], ["Floating surface", "Overlay shadow + 16–24px radius", "Menus, search results, toasts, and dialogs. Preserve focus and escape behavior."], ["Blue surfaces", "Existing AMLOK gradient or solid brand field", "White text and --on-brand-line edges. Keep shadows restrained and avoid colored glow."], ["Hover / pressed / focus", "150–200ms, no layout shift", "Change edge, fill, or shadow. Keep focus an immediate 2px outline with a 3px offset."], ["Dark theme", "Semantic foreground / surface / edge pairs", "Derived edge and shadow tokens adapt to the theme. Do not invert photography, logos, or graphics."]]}/>
        <p className="ds-callout">Rounded corners should feel designed, not inflated. Avoid glossy highlights, blur on reading panels, thick outlines, floating every element, or adding a wrapper around an already complete graphic.</p>
      </Section>

      <Section id="color" number="04" title="Calm fields. Clear signals." description="AMLOK blue anchors the identity. White and cobalt fields provide contrast; secondary colors carry specific meaning. One semantic palette supports both light and dark interfaces.">
        <div className="ds-color-grid">{colors.map(color => <button key={color.token} className="ds-swatch" onClick={() => copy(color.hex, color.name)} aria-label={`Copy ${color.name} ${color.hex}`}><span className="ds-swatch-color" style={{ background: color.hex, color: color.light ? '#101828' : '#ffffff' }}><span>{color.hex}</span><Copy size={16}/></span><strong>{color.name}</strong><code>{color.token}</code><p>{color.use}</p></button>)}</div>
        <p className="ds-note">Cobalt blue <strong>#1239B0</strong> is the supporting field for reversed logos, signal illustrations, and marketing panels. Pair it with white text. AMLOK blue <strong>#052698</strong> remains the primary identity and action color; Ink <strong>#101828</strong> remains the reading color.</p>
        <p className="ds-note">Use the shared color tokens throughout the website. Blue fields use <code>--on-brand</code> for headings, <code>--on-brand-muted</code> for supporting copy, and the paired line and surface tokens for structure. Derive tints with <code>color-mix()</code>; do not introduce separate navy panels or one-off gray and blue values.</p>
        <div className="ds-gradient-palette">
          <button className="ds-swatch ds-gradient-swatch" onClick={() => copy(heroGradient.css, heroGradient.name)} aria-label="Copy AMLOK hero gradient CSS">
            <span className="ds-swatch-color"><span>AMLOK / HERO GRADIENT</span><Copy size={16}/></span>
            <strong>{heroGradient.name}</strong><code>{heroGradient.token}</code><p>#1B4FE0 → #1140C3 → #052698</p>
          </button>
          <div className="ds-gradient-guidance"><h3>The hero field, now a palette material.</h3><p>Use this radial gradient for blue marketing surfaces and focal blue elements inside illustrations. It is the same field used by the homepage hero: a lighter center at 50% across and 42% down, falling into AMLOK blue at the edges.</p><p>Stops: <strong>#1B4FE0 at 0%</strong>, <strong>#1140C3 at 42%</strong>, and <strong>#052698 at 100%</strong>. Pair it with white or the shared on-brand text colors. Keep grid lines, signals, and motion as separate layers.</p><p className="ds-note">Use <code>background: var(--gradient-hero)</code> for CSS and the matching radial fill for SVG artwork. The logo, small interface controls, and social profile mark retain solid AMLOK blue. The downloadable token stylesheet includes this gradient.</p></div>
        </div>
        <div className="ds-panel"><div className="ds-status-samples"><Status>Selected</Status><Status tone="success">Verified</Status><Status tone="warning">Needs review</Status><Status tone="danger">Action required</Status><Status tone="neutral">Not evaluated</Status></div><p className="ds-note">Every state needs a label. Brand orange and green are accent colors; status text uses the darker semantic foreground tokens. A bright dot alone is never evidence that something is safe.</p></div>
        <Rules items={[["Light is the working default", "White supports reading and decisions. Surface gray groups related information. Keep most of the canvas neutral; reserve blue for navigation, selection, and one primary action."], ["Dark is a designed theme", "Use the theme control above to inspect the entire guide. Dark mode changes foregrounds, borders, surfaces, and status pairs together. Do not simply invert colors. Cobalt brand panels use white or pale-blue text; dark UI surfaces use the semantic theme pairs."], ["Use color with intent", "Violet distinguishes simulation. Orange draws attention. Green signals a confirmed positive state. Separate categorical charts from severity scales, and label every series."]]}/>
      </Section>


      <Section id="typography" number="05" title="A consistent voice in type." description="Inter carries the conversation. JetBrains Mono labels structured information. Use a small, repeatable hierarchy instead of resizing each section independently.">
        <div className="ds-type-specimen"><span className="ds-meta">INTER / 600</span><p>Every signal.<br />A clearer decision.</p><span className="ds-meta">JETBRAINS MONO / 500 / TRACKING 0.12EM</span><code>AMLOK / EVIDENCE 024 / REVIEW READY</code></div>
        <Specs headings={['Role', 'Desktop → mobile', 'Weight / line height', 'Use']} rows={[["Display", "64–88px → 40–48px", "600 / 1.02", "One hero per page."], ["Section heading", "48–62px; 40px compact → 32–36px", "600 / 1.08", "The same scale for every main section."], ["Feature / card heading", "24–28px → 20–24px", "600 / 1.25", "Card titles and headings under imagery."], ["UI heading", "20px", "600 / 1.3", "Panel and dialog titles."], ["Body / section description", "16–18px → 16px", "400 / 1.6", "Reading width: 45–65 characters."], ["Secondary text", "14px", "400 / 1.5", "Metadata and supporting copy."], ["Overline / telemetry", "12px", "500 / 1.4", "Monospace, short labels only."]]}/>
        <p className="ds-callout">Keep headings concise. Fit a one-line card title through column width or shorter copy before shrinking it. On narrow screens, let it wrap; never clip text or reduce it to unreadable sizes.</p>
      </Section>

      <Section id="layout" number="06" title="One width. A consistent rhythm." description="A centered, 1,280px content area anchors our marketing pages. Align section content with the logo on the left and the header action on the right. Full-width backgrounds sit outside this shared grid.">
        <BrandLayout />
        <h3 className="ds-layout-subheading">Spacing within the grid</h3>
        <div className="ds-spacing-scale">{[4, 8, 12, 16, 24, 32, 48, 64, 96].map(n => <div key={n}><i style={{ height: n }}/><code>{n}</code></div>)}</div>
        <div className="ds-layout-preview"><div className="ds-layout-columns">{Array.from({ length: 12 }, (_, i) => <i key={i}/>)}</div><div><span className="ds-meta">SHARED CONTENT WIDTH / MAX 1280PX</span><h3>One grid, from navigation to footer.</h3><p>12 columns on desktop · 8 on tablet · 4 on mobile</p></div></div>
        <Specs headings={['Relationship', 'Default', 'Responsive behavior']} rows={[["Content container", "1,280px maximum", "Use --site-content-width and auto inline margins. No additional horizontal padding on the containing section."], ["Outer gutter", "48px minimum at 1,024px and above; 20px below", "Center the content. Above 1,376px, margins grow equally while content remains 1,280px."], ["Columns", "12 desktop / 8 tablet / 4 mobile", "Desktop ≥1,024px; tablet 768–1,023px; mobile <768px. Components may stack earlier to preserve readability."], ["Narrow content", "65ch reading measure / 1,088px hero video", "Nest intentional narrow blocks inside the shared container. Keep media aspect ratios and align surrounding grids."], ["Section inset", "64–112px", "64px on mobile; use viewport-aware space when content fits."], ["Heading → description", "24px", "Keep this relationship consistent."], ["Description → actions", "24px", "Group related actions with 12–16px gaps."], ["Actions → imagery", "32–48px", "Give the visual its own clear region."], ["Image → title → body", "16px / 12px", "Use the same rhythm across feature cards."], ["Card padding / grid gap", "24–32px / 24px", "16–24px padding and 16–24px gaps on mobile. Keep text clear of rounded corners."], ["Nested surfaces", "12px inner / 20–24px outer radius", "Use 12–16px between related items. Flush media inherits the parent corner; controls keep their own radius."], ["Product density", "44px controls / 48–56px rows", "40px compact controls only with adequate target spacing."]]}/>
        <Rules items={[["One owner for the gutter", "Use the shared content-width token for navigation, section headings, card grids, sliders, and the footer. A section background spans the viewport; its inner container owns the margins. Do not add a second gutter inside it."], ["Marketing and product layouts", "Use the 1,280px frame for public pages. Product workspaces and this guide may keep a sidebar and fluid work area; apply the same spacing scale within that available region. Long-form text uses the narrower reading measure."], ["Use the available viewport", "A desktop overview can fill the area below the header when its contents fit comfortably. Allocate space to media and relationships before adding empty margins."], ["Compact desktop rhythm", "At widths of 1200px or more and heights of 820px or less, use 40px section headings, 20–24px outer insets, and 16–24px content gaps. Keep reading text at 16px, secondary copy at 14px, and interaction targets at least 44px."], ["Let content remain readable", "Sliders and long feature sections may span multiple viewports. On small screens or with larger text, use natural document flow. Never crop a section to force a viewport-height layout."], ["Keep a predictable reading path", "Stack columns in reading order. Put the image before its caption. Keep tables in their own scroll regions. A horizontal scrollbar must never appear on the whole page."]]}/>
      </Section>

      <Section id="imagery" number="07" title="Fields with structure." description="Photography adds human context; precise illustrations explain the product. Present both in softly rounded media frames with consistent spacing, preserving the artwork and its original geometry.">
        <div className="ds-grid ds-grid-2"><div className="ds-field-sample"><span className="ds-meta">AMLOK / DIRECTIONAL FIELD</span><ShieldGraphic /><strong>Clarity under pressure.</strong></div><MediaPlaceholder /></div>
        <Rules items={[["Use light to describe the object", "Keep reading surfaces solid. Within marketing artwork, a restrained Signal blue → Cobalt → AMLOK blue gradient gives a focal object dimension. Use the shared AMLOK hero radial gradient for primary blue fields. Object lighting remains consistent from the upper left; keep multicolor effects out of control borders and text."], ["Build with angular planes", "Use overlapping evidence surfaces, shallow extrusions, square scan fields, and deliberate diagonal joins that echo the logo. Preserve the original mark itself. Keep these angles inside the artwork. Use the shared 20px media radius around photography and illustration panels; avoid arbitrary silhouettes, ornamental diamonds, and unrelated 3D objects."], ["Photography and overlays", "Choose real work and real environments with cool daylight, pale blue, wood, and brick. Keep faces, hands, and the essential activity visible. Preserve the existing blue graphic overlays and corner brackets; round the photograph’s outer crop only. Credit the source below the image."], ["Protect the integrity of imagery", "Use real product screenshots with readable, sanitized sample data. Preserve aspect ratio. Do not imply a client relationship through logos without permission. Identify illustrative work as such."]]}/>
      </Section>

      <Section id="exploration" number="08" title="Shield. Signal. Scan." description="Three distinct expressions, each with a job. Their restraint is what makes the system feel precise and modern.">
        <div className="ds-motif-grid"><article><ShieldGraphic /><h3>Shield / stewardship</h3><p>A straight-edged enclosure that protects the center. Use in brand imagery and protection-related concepts.</p></article><article><div className="ds-signal-constellation"><i /><i /><i /><i /><i /><b /></div><h3>Signal / relevance</h3><p>A small dot plus a clear label. Halo, color, and intensity are supporting cues, never the entire message.</p></article><article><div className="ds-square-radar"><i /><i /><i /><b /></div><h3>Scan / discovery</h3><p>A linear pass across a square field reveals a relationship. No spinning interface or constant urgency.</p></article></div>
        <div className="ds-icon-strip">{[ShieldCheck, ScanLine, Layers3, Radio, FileText, CheckCheck].map((Icon, i) => <div key={i}><Icon size={24} strokeWidth={1.75}/><code>24 / 1.75</code></div>)}</div><p className="ds-note">Use one outline icon family, 20px or 24px on a 4px grid. Pair unfamiliar icons with text. Signal dots replace decorative diamonds. Icon-only actions require an accessible name and a 44px target.</p>
      </Section>

      <Section id="website-graphics" number="09" title="Intelligence, illustrated." description="Dimensional, precise, and unmistakably AMLOK. Square silhouettes meet directional light, layered product fragments, and vivid blue focal objects. Each workflow has a distinct visual metaphor, with the logo’s angular construction guiding the family.">
        <BrandGraphics />
        <ProductIllustrationLibrary />
        <Rules items={[["Choose the metaphor before the layout", "Begin with the action being explained. Verification can scan a document; monitoring can isolate a signal; servicing can connect a conversation with a calendar. Do not default to a chart or a dashboard card."], ["A family, not a repeated template", "Adjacent graphics must differ in silhouette, arrangement, and focal object. Repeated topics in different sections need a new viewpoint or crop. Reuse primitives and tokens, not the same finished composition."], ["Charts have a specific job", "Use a chart when a quantitative relationship, trend, or comparison is the actual subject. Do not use bars or curves as a generic symbol for intelligence, automation, or AI."], ["One graphic, one idea", "Use a few recognizable objects and one clear relationship. Keep essential explanation in the surrounding title and body. Avoid recreating an entire dashboard inside a card."], ["Give the composition a focal point", "Combine a quiet supporting plane, a clear foreground object, and one strong blue emphasis. Use overlap and scale to establish depth. Background records may recede; the focal object and its labels stay crisp. Reserve warm accents for a labeled point of attention."], ["Motion supports the story", "Loop decorative illustrations automatically while visible. Keep values and outer captions steady; a complete illustrative object may drift up to 5px to suggest depth. Pause work offscreen and show a complete static composition for reduced motion. Essential information must never depend on an animation."]]}/>
        <Specs headings={['Graphic anatomy', 'Standard', 'Application']} rows={[["Frame and field", "20px media shell · original interior geometry", "Round the presentation frame only. Inside artwork, preserve ceramic-white planes, cobalt focal faces, sharp edges, and existing lighting. No extra decorative backplate."], ["Material and depth", "Shared ceramic / cobalt gradients · 2px contact + 12px lift shadow", "Use the live illustration library as the source. Limit depth to a few meaningful layers. Fine edges stay sharp; shadows separate objects without becoming a glow."], ["Angular construction", "Straight edges · shallow extrusions · purposeful diagonal joins", "Derive the feeling from the logo’s solid faces and negative space. Keep the logo intact. Diagonals belong inside conceptual graphics, never on control hit areas."], ["Visual spacing", "24px inset · 8–12px internal gaps · 16–24px to caption", "Keep a consistent 250–320px graphic height within a row. Recompose on mobile rather than scaling all the text down."], ["Lines and marks", "1px grid · 2–2.5px chart line · small signal dots", "Use blue for the main series. Circles belong to data marks and proportion charts. The enclosing media shell uses the shared radius; the artwork remains unchanged."], ["Color and state", "Canvas / surface / ink / muted / blue / signal blue", "Use labeled warning and success pairs. Hatch or dash expected values so meaning does not depend on color."], ["Type and explanation", "Inter for labels and captions · JetBrains Mono for short telemetry", "Keep essential copy outside the illustration at the normal body size. Tiny sample labels are supporting texture, never the only explanation."], ["Data integrity", "Observed, expected, and illustrative remain distinct", "Use fictional sample records. Label units and periods when showing data; never imply a live decision or validated outcome."], ["Responsive delivery", "HTML / CSS / SVG · shared illustration components", "Preserve line sharpness, semantic colors, and aspect ratio. Provide an accessible description when the graphic adds information."], ["Animation cadence", "4–8s for decorative loops · 14s for background data", "Use linear scans, traveling signals, or a 5px depth drift. Scenario twins may shift 10px to compare layers. No spinning radar, flashing alerts, springy bouncing, or changing financial claims."]]}/>
        <div className="ds-grid ds-grid-2"><article className="ds-panel"><span className="ds-meta">USE</span><h3>A recognizable financial story.</h3><p>Identity documents, policy gates, square signal fields, source citations, conversation threads, portfolio twins, and embedded modules. Choose the object that explains the subject. Keep the story calm enough to understand at a glance.</p></article><article className="ds-panel"><span className="ds-meta">AVOID</span><h3>Decoration without meaning.</h3><p>Flat wireframes with no focal point, the same dashboard in every card, unrelated 3D objects, rainbow gradients, floating glass, giant glowing shields, ornamental diamonds, and dense mock interfaces that cannot be read.</p></article></div>
        <p className="ds-callout">Consistency comes from the visual grammar, not identical graphics. Reuse our color, geometry, typography, line weights, and motion behavior; invent the composition around the job each component explains.</p>
      </Section>

      <Section id="components" number="10" title="Controls that make sense." description="Rounded controls share the same borders, spacing, states, and behavior. These are working examples: try validation, keyboard tabs, theme switching, and the review dialog.">
        <ComponentLab onOpen={() => dialogRef.current?.showModal()} onNotice={notify}/>
        <FieldPatterns />
        <Specs headings={['Pattern', 'Required states', 'Behavior']} rows={[["Button / icon action", "Default, hover, focus, pressed, disabled, loading", "Keep labels visible while loading. Prevent duplicate submission."], ["Input / textarea / select", "Empty, filled, focused, invalid, disabled, read-only", "Persistent label, helper text, inline error; preserve entered data."], ["Checkbox / switch", "On, off, focus, disabled", "4px checkbox for selection; rounded track and circular switch thumb for an immediate setting."], ["Tabs / navigation", "Selected, hover, focus", "Visible underline or left rail; keyboard navigation and semantic selected state."], ["Dialog / drawer", "Open, pending, error, complete", "Move focus in, contain it, support Escape, restore focus on close."], ["Toast / inline message", "Success, information, warning, error", "Announce without stealing focus. Keep critical errors until resolved."], ["Menu / popover / tooltip", "Open, selected, focus", "16px rounded surface. Dismiss with Escape; use labels rather than tooltip-only instructions."]]}/>
      </Section>

      <Section id="data" number="11" title="Built for real work." description="Dense information can still be calm. Keep the table, the selected record, and its evidence in one understandable workspace.">
        <DataWorkspace /><ChartSpecimen />
        <Rules items={[["Make uncertainty visible", "Show source date, freshness, missing fields, and unavailable values. A dash means unavailable; zero means zero. Never hide a stale result behind a green status."], ["Keep context during change", "Filtering, sorting, and opening a record preserve the user’s place. For bulk actions, show the selected count, scope, and a review step for consequential changes."], ["Design the complete lifecycle", "Each workflow needs initial, loading, partial, empty, error, recovery, and completed states. Include permissions, audit history, and a safe way to return to the prior view."]]}/>
      </Section>

      <Section id="ai" number="12" title="Intelligence with human control." description="AMLOK organizes evidence and surfaces signals. The institution owns its policies, customer relationship, and final decision.">
        <div className="ds-ai-flow"><span>01 / SOURCE EVIDENCE</span><ArrowRight size={20}/><span>02 / AI ASSESSMENT</span><ArrowRight size={20}/><span>03 / HUMAN DECISION</span></div>
        <div className="ds-ai-example"><div><Status tone="warning">Illustrative · review required</Status><h3>Ownership evidence is incomplete.</h3><p>The declaration names two owners. The registry excerpt confirms one. Request the missing ownership evidence before completing verification.</p><div className="ds-ai-sources"><span><FileText size={16}/>Ownership declaration · example page 2</span><span><FileText size={16}/>Registry excerpt · example record</span></div></div><aside><span className="ds-meta">HUMAN REVIEW</span><h4>Next step</h4><p>Inspect sources, request evidence, or record an approved exception with a reason.</p><strong>No final credit decision made.</strong></aside></div>
        <Specs headings={['Requirement', 'Interface treatment']} rows={[["Evidence before confidence", "Link each material claim to its source. Separate extracted facts, interpretations, and recommendations."], ["Honest uncertainty", "State what is missing or contradictory. Do not invent confidence percentages or guarantee outcomes."], ["Explicit authority", "Label AI-generated content. Consequential actions require an authorized reviewer and a visible confirmation."], ["Controllable execution", "Show task progress, cancel/retry controls, and completed actions. Do not imply a task is finished while it is still running."], ["Auditable decisions", "Record reviewer, time, policy version, evidence, overrides, and reason. Explain access restrictions without exposing protected data."]]}/>
      </Section>

      <Section id="marketing" number="13" title="One brand, every surface." description="Use the same grid, typography, rounded surfaces, and precise signal graphics in a website, campaign, presentation, or research publication.">
        <div className="ds-marketing-grid"><article className="ds-campaign ds-campaign-hero"><Wordmark /><span className="ds-meta">RISK INTELLIGENCE / AMLOK</span><h3>Capital moves.<br />Intelligence keeps up.</h3><div className="ds-campaign-rule"/><p>Your team owns the final decision.</p><ShieldGraphic /><span className="ds-campaign-format">WEB / PRESENTATION · 16:9</span></article><article className="ds-campaign ds-campaign-research"><Wordmark /><span className="ds-meta">RESEARCH / WORKING PAPER</span><h3>Seeing risk<br />in the<br />relationships.</h3><div className="ds-publication-grid"/><span className="ds-campaign-format">RESEARCH / SOCIAL · 1:1</span></article></div>
        <Specs headings={['Surface', 'Composition', 'Delivery']} rows={[["Website", "One clear proposition, one primary action, evidence below", "Shared 1,280px grid; 48px minimum desktop margins, 20px below 1,024px; responsive images; semantic headings."], ["Presentation", "One message per slide; large chart labels; restrained signal accents", "1920 × 1080 / 16:9. Keep content 64px from edges."], ["Social / link preview", "Short headline, mark, one visual field", "1080 × 1080 or 1200 × 630. Keep text within a 64px safe area."], ["Research / PDF", "Structured headings, numbered figures, sources, and a clear methodology", "Accessible text, selectable charts, publication date and version."], ["Email", "One column, concise copy, one primary action", "600px content width; 16px text; live text buttons and alt text."]]}/>
        <p className="ds-callout">Case studies describe methodology, evidence, limitations, and what was retrospectively evaluated. Never describe planned validation as completed work, or use “trusted by” for institutions that are only research subjects.</p>
      </Section>

      <Section id="voice" number="14" title="Precise. Direct. Accountable." description="Write like an experienced colleague. Explain the signal, its source, and the next useful action. Avoid hype and certainty that the evidence cannot support.">
        <Specs headings={['Use', 'Avoid']} rows={[["Review the ownership evidence.", "Unlock next-generation verification magic."], ["Three transactions need review.", "Suspicious borrower detected."], ["The source is unavailable. Your previous result is saved. Retry the connection.", "Something went wrong."], ["AI-generated assessment · awaiting review", "Approved by AI"], ["Your team owns the final decision.", "Risk-free decisions, guaranteed."]]}/>
        <Rules items={[["Names and headings", "Use AMLOK in written copy. Use sentence case for headings, buttons, and navigation. Reserve uppercase monospace for short category labels, IDs, and telemetry."], ["Clear actions and errors", "Name the outcome: Review evidence, Request documents, Save changes. Errors explain what happened and how to recover without blaming the user."], ["Consistent financial language", "Use explicit currency, timezone, units, and dates when ambiguity matters. Keep precision appropriate to the source. Do not present an estimate as an observed value."]]}/>
      </Section>

      <Section id="motion" number="15" title="Motion reveals information." description="The scan is a linear discovery gesture. Transitions connect states and guide attention. Motion never becomes the work the user has to manage.">
        <div className="ds-motion-stage"><RadarVisual paused={paused}/><div><span className="ds-meta">SIGNAL SCAN / 4000MS</span><h3>A measured reveal.</h3><p>Start the sample to see the scan pass through a square field. Animation pauses outside the viewport. Reduced-motion preferences keep it static.</p><button className="ds-button ds-button-secondary" aria-pressed={!paused} onClick={() => setPaused(!paused)}>{paused ? <Play size={16}/> : <Pause size={16}/>} {paused ? 'Play scan' : 'Pause scan'}</button></div></div>
        <Specs headings={['Timing', 'Use', 'Constraint']} rows={[["150ms", "Hover, focus, selection feedback", "No movement needed to indicate focus."], ["200ms", "Tabs, disclosure, small state transitions", "Prefer opacity and a maximum 4px translation."], ["400ms", "Section or illustration entrance", "Run once. Never delay access to content."], ["4000ms", "Optional marketing scan", "In view only; pause control; static under reduced motion."], ["4–8s / website graphics", "Decorative chart and signal loops", "Automatic in view; values stay fixed; static under reduced motion. Whole illustrative objects may move gently. See Website graphics for patterns."], ["0ms / reduced motion", "Immediate final state", "Disable pulses, scans, parallax, and smooth scroll."]]}/>
      </Section>

      <Section id="accessibility" number="16" title="Access is part of the design." description="Target WCAG 2.2 AA. These requirements guide delivery; a design system alone does not certify an implementation.">
        <Rules items={[["Readable contrast", "Normal text needs at least 4.5:1; large text 3:1. Meaningful controls and graphical boundaries need 3:1. Check every foreground/background pair, including disabled-adjacent helper text and dark mode."], ["Visible keyboard access", "Use native controls and a 2px focus outline with a 3px offset. Ensure sticky headers do not hide focused items. Support Escape and return focus after overlays."], ["Comfortable targets", "Prefer 44 × 44px targets. Use adequate spacing for compact controls; do not confuse the preferred size with WCAG’s 24px minimum target rule and its exceptions."], ["Reflow without loss", "Test 320px width, 200% text resizing, and browser zoom. Preserve reading order and let content grow. Data tables may scroll within a labeled region."], ["Meaning beyond color", "Use text, icon shape, and selected-state semantics together. Announce validation and asynchronous results. Provide descriptive labels and meaningful image alternatives."], ["User preferences", "Respect reduced motion and forced colors. Do not put essential text in an image. Avoid autoplaying audio, flashing content, and decorative animation in task-critical views."]]}/>
        <div className="ds-reference-links"><a href="https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html" target="_blank" rel="noreferrer">Contrast guidance ↗</a><a href="https://www.w3.org/WAI/ARIA/apg/patterns/tabs/" target="_blank" rel="noreferrer">Keyboard patterns ↗</a><a href="https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html" target="_blank" rel="noreferrer">Target size guidance ↗</a></div>
      </Section>


      <Section id="implementation" number="17" title="A system that stays coherent." description="The same token source powers this guide, the website, and the downloadable stylesheet. Change a foundation once, then validate its effects across components and themes.">
        <div className="ds-implementation-actions"><a className="ds-button" href="/brand/amlok-tokens.txt" download="amlok-tokens.css"><Download size={16}/>Download CSS tokens</a><button className="ds-button ds-button-secondary" onClick={() => copy(tokensCSS, 'Design tokens')}><Copy size={16}/>Copy tokens</button><span className="ds-note">v{brand.version} · Reviewed {brand.reviewed}</span></div>
        <div className="ds-token-groups">{Object.entries(tokenGroups).map(([group, tokens]) => <details key={group}><summary>{group}<span>{Object.keys(tokens).length} tokens</span></summary><div className="ds-spec-scroll"><table className="ds-spec-table"><thead><tr><th>Token</th><th>Value</th></tr></thead><tbody>{Object.entries(tokens).map(([key, value]) => <tr key={key}><td><code>{key}</code></td><td><code>{value}</code></td></tr>)}</tbody></table></div></details>)}</div>
        <Rules items={[["Build with semantic tokens", "Use canvas, surface, ink, muted, line, action, and status pairs. Keep theme overrides together. Avoid new one-off radii, colors, or spacing values for individual sections."], ["Review before adding a pattern", "Document its purpose, anatomy, states, keyboard behavior, responsive behavior, and content rules. Reuse a current pattern when it solves the same problem."], ["Ship with evidence", "Review design, content, and implementation together. Check desktop and mobile, both themes, keyboard, reduced motion, errors, and loading. Record exceptions and their reason."]]}/>
        <Specs headings={['Governance', 'Standard']} rows={[["Foundation changes", "Update tokens and this guide first. Review impact on all consuming components."], ["Component changes", "Document anatomy, interaction, density, and states; include a working specimen."], ["Versioning", "Major for breaking token/behavior changes; minor for compatible patterns; patch for corrections."], ["Ownership", "Design owns visual rules; engineering owns behavior; content owners approve claims; accessibility is shared."], ["Version 2.0", "Rounded interface system: shared radius hierarchy, pill marketing actions, subtle semantic edges, layered shadows, and updated control, media, and spacing guidance. Logo, palette, hero field, photography, and illustration compositions are preserved."], ["Version 1.5", "Shared marketing layout: 1,280px maximum content width, 48px desktop / 20px compact gutters, aligned header and sections, and a responsive width comparison in Layout & spacing."], ["Version 1.3.1", "Hero radial gradient added to the color palette and downloadable tokens, with matching CSS and SVG fills. Applied to blue fields in Risk operations without changing the section layout or motion."], ["Version 1.3", "Dimensional website illustrations: ceramic surfaces, directional cobalt light, angular layers, subject-specific compositions, compact variants, and motion with a static reduced-motion state."], ["Version 1.2", "Cobalt blue replaces Deep navy in brand panels, identity previews, radar examples, and campaign samples. Ink remains #101828. Use --blue-field; --navy is a compatibility alias."], ["Version 1.1", "Website graphics library with shared live illustrations, composition rules, semantic colors, and continuous decorative motion."], ["Version 1.0", "Unified square geometry, semantic light/dark themes, signal/shield language, component states, enterprise workflows, and marketing templates."], ["Attribution", "Applicable component, icon, and font licenses are included with the downloadable assets."]]}/>
      </Section>
      <footer className="ds-footer"><Wordmark /><p>{brand.principle}</p><a href="#overview">Back to overview ↑</a></footer>
    </main>
    <div className="ds-toast" role="status" aria-live="polite" data-visible={!!notice}>{notice && <><Check size={18}/>{notice}<button aria-label="Dismiss notification" onClick={() => setNotice('')}><X size={16}/></button></>}</div>
    <dialog className="ds-dialog" ref={dialogRef} aria-labelledby="ds-dialog-title" aria-describedby="ds-dialog-description"><div className="ds-dialog-header"><span className="ds-meta">REVIEW / COMPONENT PREVIEW</span><button className="ds-icon-button" aria-label="Close review dialog" onClick={() => dialogRef.current?.close()}><X size={20}/></button></div><h2 id="ds-dialog-title">Ready for human review.</h2><p id="ds-dialog-description">The evidence is organized. Your team owns the final decision. This is a local design-system example.</p><Status tone="warning">Review required</Status><div className="ds-dialog-actions"><button className="ds-button ds-button-secondary" onClick={() => dialogRef.current?.close()}>Cancel</button><button className="ds-button" onClick={() => { dialogRef.current?.close(); notify('Preview review recorded. No real decision was made.'); }}>Record review <Check size={16}/></button></div></dialog>
  </div>;
}

return <BrandSystem/>;
};
