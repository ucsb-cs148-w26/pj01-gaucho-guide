export function Footer() {
  return (
    <footer className="w-full border-t border-border bg-background px-6 py-12">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col items-center gap-6 text-center">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center">
              <svg viewBox="0 0 24 24" className="h-6 w-6" fill="#7C3AED">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#7C3AED" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="text-xl font-bold text-foreground italic">GauchoGuide</span>
          </div>

          {/* Tagline */}
          <p className="max-w-md text-sm text-muted-foreground">
            Your personal UCSB academic strategist. Built by students, for students.
          </p>

          {/* Links */}
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">About</a>
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">Privacy</a>
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">Terms</a>
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">Contact</a>
          </div>

          {/* Copyright */}
          <p className="text-xs text-muted-foreground">
            © 2026 GauchoGuide. Not affiliated with UC Santa Barbara.
          </p>
        </div>
      </div>
    </footer>
  )
}
