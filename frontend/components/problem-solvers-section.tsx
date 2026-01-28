"use client"

import { Sparkles, Target, Compass } from "lucide-react"

const features = [
  {
    icon: Sparkles,
    title: "Break down problems together",
    description: "GauchoGuide builds on your ideas, expands on your logic, and simplifies complexity one step at a time."
  },
  {
    icon: Target,
    title: "Tackle your toughest coursework",
    description: "GauchoGuide provides expert-level collaboration on the things you need to get done—from course selection to graduation planning."
  },
  {
    icon: Compass,
    title: "Explore what's next",
    description: "Like an expert in your pocket, collaborating with GauchoGuide expands what you can build on your own or with teams."
  }
]

const networkNodes = [
  { label: "Course Planning", x: 55, y: 35, primary: true },
  { label: "Major Requirements", x: 75, y: 25, primary: true },
  { label: "Prerequisites", x: 45, y: 20, primary: false },
  { label: "Schedules", x: 35, y: 30, primary: false },
  { label: "GE Requirements", x: 60, y: 50, primary: false },
  { label: "Electives", x: 80, y: 40, primary: false },
  { label: "Career Paths", x: 70, y: 60, primary: true },
  { label: "Internships", x: 85, y: 55, primary: false },
  { label: "Research", x: 50, y: 65, primary: false },
  { label: "Minors", x: 40, y: 55, primary: false },
  { label: "Double Major", x: 25, y: 45, primary: false },
  { label: "Study Abroad", x: 90, y: 70, primary: false },
  { label: "Graduate School", x: 65, y: 75, primary: false },
]

export function ProblemSolversSection() {
  return (
    <section className="w-full bg-background px-6 py-16 lg:py-24">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-12 text-center">
          <h2 className="font-serif text-4xl font-bold text-foreground lg:text-5xl text-balance">
            The AI for UCSB students
          </h2>
          
          {/* Download/App buttons */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <span className="text-sm text-muted-foreground">Start planning today:</span>
            <button className="rounded-full border border-border bg-card px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary">
              Web App
            </button>
            <button className="rounded-full border border-border bg-card px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary">
              iOS
            </button>
            <button className="rounded-full border border-border bg-card px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary">
              Android
            </button>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid gap-12 lg:grid-cols-3">
          {/* Features Column */}
          <div className="flex flex-col gap-8 lg:col-span-1">
            {features.map((feature, index) => (
              <div key={index} className="flex flex-col gap-3 border-l-2 border-border pl-4 transition-colors hover:border-primary">
                <div className="flex items-center gap-2">
                  <feature.icon className="h-5 w-5 text-muted-foreground" />
                  <h3 className="font-semibold text-foreground">{feature.title}</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>

          {/* Network Diagram */}
          <div className="relative lg:col-span-2 h-96 lg:h-auto">
            {/* Center Logo */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center">
                <svg viewBox="0 0 24 24" className="h-6 w-6" fill="#7C3AED">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#7C3AED" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <span className="font-bold text-foreground italic">GauchoGuide</span>
            </div>

            {/* Network Nodes */}
            {networkNodes.map((node, index) => (
              <div
                key={index}
                className="absolute text-xs lg:text-sm"
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
              >
                <span className={node.primary ? "font-semibold text-foreground" : "text-muted-foreground"}>
                  {node.label}
                </span>
              </div>
            ))}

            {/* Connection Lines SVG */}
            <svg className="absolute inset-0 h-full w-full" style={{ zIndex: -1 }}>
              {networkNodes.map((node, index) => (
                <line
                  key={index}
                  x1="50%"
                  y1="50%"
                  x2={`${node.x}%`}
                  y2={`${node.y}%`}
                  stroke="#e0ddd5"
                  strokeWidth="1"
                />
              ))}
            </svg>
          </div>
        </div>
      </div>
    </section>
  )
}
