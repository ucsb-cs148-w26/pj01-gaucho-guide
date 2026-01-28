"use client"

import { useState } from "react"
import { ChevronDown } from "lucide-react"

export function Header() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <header className="w-full border-b border-border/50 bg-background">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <nav className="flex items-center gap-8">
          <span className="text-sm font-medium text-foreground/80 hover:text-foreground cursor-pointer">
            Product
          </span>
        </nav>

        <div className="flex items-center gap-2">
          <button 
            className="flex items-center gap-1 text-sm font-medium text-foreground/80 hover:text-foreground"
            onClick={() => setIsOpen(!isOpen)}
          >
            Explore here
            <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  )
}
