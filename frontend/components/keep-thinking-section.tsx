"use client"

import { Play, ArrowUp } from "lucide-react"

export function KeepThinkingSection() {
  return (
    <section className="w-full bg-background px-6 py-16 lg:py-24">
      <div className="mx-auto max-w-7xl">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center">
            <svg viewBox="0 0 24 24" className="h-10 w-10" fill="none" stroke="#1a1a1a" strokeWidth="1.5">
              <path d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        </div>

        {/* Header */}
        <h2 className="mb-12 text-center font-serif text-4xl font-bold text-foreground lg:text-5xl text-balance">
          Keep planning with GauchoGuide
        </h2>

        {/* Video Placeholder */}
        <div className="relative mx-auto max-w-4xl overflow-hidden rounded-2xl bg-gradient-to-br from-teal-200 to-teal-400">
          <div className="aspect-video w-full">
            <img
              src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1200&h=675&fit=crop"
              alt="Students studying at university campus"
              className="h-full w-full object-cover"
            />
            {/* Play Button Overlay */}
            <div className="absolute inset-0 flex items-center justify-center bg-black/20">
              <button className="flex h-16 w-16 items-center justify-center rounded-xl bg-card/90 shadow-lg transition-transform hover:scale-105">
                <Play className="h-6 w-6 text-foreground ml-1" fill="currentColor" />
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Content */}
        <div className="mt-12 grid gap-8 lg:grid-cols-2">
          <div>
            <h3 className="font-serif text-2xl font-bold text-foreground">
              Your academic journey's collaborator
            </h3>
          </div>
          <div>
            <p className="text-muted-foreground leading-relaxed">
              There's never been a worse time to be confused about your major, or a better time to have a personalized academic advisor.
            </p>
          </div>
        </div>

        {/* Secondary Search Box */}
        <div className="mt-16 rounded-2xl border border-border bg-card p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <h3 className="font-serif text-2xl font-bold text-foreground">
              What problem are you up against?
            </h3>
            <div className="flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2">
              <input
                type="text"
                placeholder="How can I help you today?"
                className="w-64 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
              />
              <button className="flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-accent">
                Ask GauchoGuide
                <ArrowUp className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
