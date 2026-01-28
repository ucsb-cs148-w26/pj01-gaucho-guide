import { Cloud, ArrowRight, Sparkles } from "lucide-react"

const features = [
  {
    name: "Course Reviews",
    description: "Most comprehensive source for your course planning decisions",
    tags: ["Professor ratings", "Difficulty scores", "Grade distributions"],
  },
  {
    name: "Major Requirements",
    description: "Powerful and detailed tracking, designed for the major you're in",
    tags: ["Prerequisite chains", "Unit tracking", "GE requirements"],
  },
  {
    name: "Schedule Planning",
    description: "Fastest planner, optimized for your most productive schedule",
    tags: ["Time conflicts", "Workload balance", "Gold sync"],
  },
]

const latestFeatures = [
  { name: "CS Course Roadmap 2026", label: "New Feature" },
  { name: "Professor Sentiment Analysis", label: "Update" },
  { name: "4-Year Plan Generator", label: "Popular" },
]

export function ModelsSection() {
  return (
    <section className="w-full bg-secondary/30 px-6 py-16 lg:py-24">
      <div className="mx-auto max-w-7xl">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <Cloud className="h-10 w-10 text-muted-foreground" />
        </div>

        {/* Header */}
        <h2 className="mb-12 text-center font-serif text-4xl font-bold text-foreground lg:text-5xl">
          GauchoGuide features
        </h2>

        {/* Feature Cards */}
        <div className="space-y-4">
          {features.map((feature, index) => (
            <div
              key={index}
              className="rounded-2xl border border-border bg-card p-6 transition-shadow hover:shadow-md lg:p-8"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex-1">
                  <h3 className="font-serif text-2xl font-bold text-foreground lg:text-3xl">
                    {feature.name}
                  </h3>
                </div>
                <div className="flex-1">
                  <p className="mb-3 font-medium text-foreground">{feature.description}</p>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                    {feature.tags.map((tag, tagIndex) => (
                      <span key={tagIndex}>
                        {tag}
                        {tagIndex < feature.tags.length - 1 && (
                          <span className="ml-2">•</span>
                        )}
                      </span>
                    ))}
                  </div>
                  <button className="mt-4 flex items-center gap-2 rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary">
                    Feature details
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="my-16 border-t border-border" />

        {/* Latest Releases */}
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center">
              <svg viewBox="0 0 24 24" className="h-8 w-8" fill="none" stroke="#1a1a1a" strokeWidth="1.5">
                <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <h3 className="font-serif text-xl font-bold text-foreground lg:text-2xl">
                Explore the<br />latest features
              </h3>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="space-y-6">
              {latestFeatures.map((feature, index) => (
                <div key={index} className="group cursor-pointer">
                  <h4 className="font-serif text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                    {feature.name}
                  </h4>
                  <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                    <Sparkles className="h-4 w-4" />
                    {feature.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
