import { Header } from "@/components/header"
import { HeroSection } from "@/components/hero-section"
import { ProblemSolversSection } from "@/components/problem-solvers-section"
import { HowToUseSection } from "@/components/how-to-use-section"
import { KeepThinkingSection } from "@/components/keep-thinking-section"
import { ModelsSection } from "@/components/models-section"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <HeroSection />
      <ProblemSolversSection />
      <HowToUseSection />
      <KeepThinkingSection />
      <ModelsSection />
      <Footer />
    </main>
  )
}
