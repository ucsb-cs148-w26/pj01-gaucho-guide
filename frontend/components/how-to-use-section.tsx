"use client"

import { useState } from "react"
import { GraduationCap, Code, Search, BarChart3, Lightbulb } from "lucide-react"

const tabs = [
  { id: "learn", label: "Learn", icon: GraduationCap },
  { id: "code", label: "Code", icon: Code },
  { id: "research", label: "Research", icon: Search },
  { id: "analyze", label: "Analyze", icon: BarChart3 },
  { id: "create", label: "Create", icon: Lightbulb },
]

const tabContent: Record<string, { prompt: string; attachments: { name: string; size: string; type: string }[]; output: { title: string; items: string[] }[] }> = {
  learn: {
    prompt: "Design a comprehensive study guide with summaries, practice questions, and memory aids from my course materials.",
    attachments: [
      { name: "Study notes", size: "4 mb", type: "doc" },
      { name: "CS32 Syllabus", size: "1.2", type: "pdf" },
    ],
    output: [
      { title: "Table of contents", items: ["Course overview", "Lecture 1: Data Structures", "Lecture 2: Algorithms", "Practice questions", "Study strategies"] },
      { title: "Course overview", items: ["Meeting times: MWF 10:10-11:00 AM, Lab Tuesdays 2:00-4:50 PM", "Office hours: Tuesdays 1-3 PM, Thursdays 11 AM-1 PM"] },
      { title: "Key dates to remember", items: ["February 21: Midterm exam 1", "March 7: Project 1 due", "April 4: Midterm exam 2", "May 12: Final exam (8:00-11:00 AM)"] },
      { title: "Grade breakdown", items: ["Midterm exam 1: 20%", "Midterm exam 2: 20%", "Final exam: 30%"] },
    ]
  },
  code: {
    prompt: "Help me debug this recursive function and explain the time complexity.",
    attachments: [
      { name: "main.cpp", size: "2 kb", type: "cpp" },
      { name: "test_cases.txt", size: "512 b", type: "txt" },
    ],
    output: [
      { title: "Code analysis", items: ["Function overview", "Bug identified", "Fixed implementation", "Time complexity analysis"] },
      { title: "Bug found", items: ["Base case not handling edge case", "Off-by-one error in loop", "Memory leak in recursion"] },
    ]
  },
  research: {
    prompt: "Find the best professors for CS courses based on student reviews and teaching style.",
    attachments: [],
    output: [
      { title: "Top rated professors", items: ["Prof. Smith - CS16 (4.8/5)", "Prof. Johnson - CS32 (4.7/5)", "Prof. Williams - CS64 (4.6/5)"] },
      { title: "Research findings", items: ["Teaching style comparisons", "Course difficulty ratings", "Student recommendations"] },
    ]
  },
  analyze: {
    prompt: "Analyze my transcript and suggest the optimal course sequence for next quarter.",
    attachments: [
      { name: "Transcript.pdf", size: "856 kb", type: "pdf" },
    ],
    output: [
      { title: "Analysis summary", items: ["Completed requirements", "Remaining requirements", "Recommended courses", "Workload balance"] },
      { title: "Recommendations", items: ["Take CS130A before CS130B", "Complete GE requirements", "Consider research opportunities"] },
    ]
  },
  create: {
    prompt: "Create a 4-year graduation plan for a Computer Science major with a minor in Statistics.",
    attachments: [],
    output: [
      { title: "Year 1", items: ["Fall: CS16, Math 3A, Writing 2", "Winter: CS24, Math 3B, GE", "Spring: CS32, Math 4A, GE"] },
      { title: "Year 2", items: ["Fall: CS64, CS40, PSTAT 120A", "Winter: CS130A, PSTAT 120B, GE", "Spring: CS130B, PSTAT 120C, Elective"] },
    ]
  },
}

export function HowToUseSection() {
  const [activeTab, setActiveTab] = useState("learn")
  const content = tabContent[activeTab]

  return (
    <section className="w-full bg-background px-6 py-16 lg:py-24">
      <div className="mx-auto max-w-7xl">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center">
            <svg viewBox="0 0 24 24" className="h-10 w-10" fill="none" stroke="#1a1a1a" strokeWidth="1.5">
              <path d="M9 12h.01M15 12h.01M12 12h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M8 9l2-2 2 2M14 9l2-2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        </div>

        {/* Header */}
        <h2 className="mb-12 text-center font-serif text-4xl font-bold text-foreground lg:text-5xl text-balance">
          How you can use GauchoGuide
        </h2>

        {/* Tabs */}
        <div className="mb-8 flex flex-wrap justify-center gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-card border border-border shadow-sm text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Card */}
        <div className="overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/20 to-primary/5">
          <div className="grid lg:grid-cols-2">
            {/* Left - Input Side */}
            <div className="relative p-8 lg:p-12">
              {/* Decorative wavy lines */}
              <div className="absolute inset-0 opacity-20">
                <svg className="h-full w-full" viewBox="0 0 400 400" fill="none">
                  <path d="M0 100 Q100 80 200 100 T400 100" stroke="#7C3AED" strokeWidth="2" />
                  <path d="M0 200 Q100 180 200 200 T400 200" stroke="#7C3AED" strokeWidth="2" />
                  <path d="M0 300 Q100 280 200 300 T400 300" stroke="#7C3AED" strokeWidth="2" />
                </svg>
              </div>

              <div className="relative space-y-4">
                {/* Prompt Card */}
                <div className="rounded-xl bg-foreground/90 p-4 text-card">
                  <p className="mb-2 text-xs font-medium text-card/70">Prompt</p>
                  <p className="text-sm leading-relaxed">{content.prompt}</p>
                </div>

                {/* Attachments */}
                {content.attachments.length > 0 && (
                  <div className="rounded-xl bg-foreground/90 p-4 text-card">
                    <p className="mb-3 text-xs font-medium text-card/70">Attachments</p>
                    <div className="grid grid-cols-2 gap-2">
                      {content.attachments.map((attachment, index) => (
                        <div key={index} className="rounded-lg bg-foreground/50 p-3">
                          <p className="text-sm font-medium">{attachment.name}</p>
                          <p className="text-xs text-card/60">{attachment.size}</p>
                          <p className="mt-2 text-xs text-card/40">{attachment.type}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right - Output Side */}
            <div className="bg-secondary/80 p-8 lg:p-12">
              <div className="space-y-6">
                {content.output.map((section, index) => (
                  <div key={index}>
                    <h3 className="mb-3 font-serif text-xl font-bold text-foreground">{section.title}</h3>
                    <ul className="space-y-2">
                      {section.items.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-start gap-2 text-sm text-muted-foreground">
                          <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Label */}
        <div className="mt-8 text-center">
          <h3 className="font-serif text-2xl font-bold text-foreground">{tabs.find(t => t.id === activeTab)?.label}</h3>
          <p className="mt-2 text-muted-foreground">
            Learn anything through conversation. Upload docs or images for personalized guidance.
          </p>
        </div>
      </div>
    </section>
  )
}
