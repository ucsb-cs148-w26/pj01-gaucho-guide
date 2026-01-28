"use client"

import { ArrowUp, Pencil, BookOpen, Code } from "lucide-react"
import { CompassIllustration } from "./compass-illustration"

export function HeroSection() {
  return (
    <section className="relative w-full overflow-hidden bg-background px-6 py-16 lg:py-24">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-8 items-center">
          {/* Left Content */}
          <div className="flex flex-col gap-8">
            <div className="flex flex-col gap-4">
              <h1 className="font-serif text-5xl font-bold leading-tight tracking-tight text-foreground lg:text-6xl text-balance">
                Your personal UCSB academic strategist.
              </h1>
              <p className="text-lg text-muted-foreground lg:text-xl">
                Review courses, map your major path, and navigate UCSB with confidence.
              </p>
            </div>

            {/* Search Input */}
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 shadow-sm">
                <input
                  type="text"
                  placeholder="What class should I take after CS16?"
                  className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
                />
                <button className="flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-accent">
                  Ask GauchoGuide
                  <ArrowUp className="h-4 w-4" />
                </button>
              </div>

              {/* Quick Action Tags */}
              <div className="flex flex-wrap gap-2">
                <button className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-foreground transition-colors hover:bg-secondary">
                  <Pencil className="h-4 w-4" />
                  Plan
                </button>
                <button className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-foreground transition-colors hover:bg-secondary">
                  <BookOpen className="h-4 w-4" />
                  Review
                </button>
                <button className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-foreground transition-colors hover:bg-secondary">
                  <Code className="h-4 w-4" />
                  Explore
                </button>
              </div>
            </div>

            {/* Feature Card */}
            <div className="max-w-xs rounded-xl border border-border bg-card p-4 shadow-sm">
              <p className="text-sm font-medium text-foreground">
                Go from rough schedule to real plan with GauchoGuide
              </p>
              <div className="mt-3 flex items-center gap-2 rounded-lg bg-secondary/50 p-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                  <div className="h-4 w-4 rounded-full bg-primary" />
                </div>
                <div className="h-3 w-16 rounded bg-muted" />
              </div>
            </div>
          </div>

          {/* Right Illustration */}
          <div className="flex items-center justify-center lg:justify-end">
            <CompassIllustration />
          </div>
        </div>
      </div>
    </section>
  )
}
