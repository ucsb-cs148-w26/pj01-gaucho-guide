export function CompassIllustration() {
  return (
    <svg
      viewBox="0 0 400 400"
      className="h-80 w-80 lg:h-96 lg:w-96"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Purple accent circle */}
      <circle cx="280" cy="100" r="40" fill="#7C3AED" />
      
      {/* Abstract pathway/compass lines */}
      <path
        d="M50 350 Q100 300 150 280 T250 200 Q300 180 350 160 Q380 140 350 100"
        stroke="#1a1a1a"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      
      {/* Compass-like swirl */}
      <path
        d="M200 200 Q220 180 240 200 Q260 220 240 240 Q220 260 200 240 Q180 220 200 200 Z"
        stroke="#1a1a1a"
        strokeWidth="4"
        fill="none"
      />
      
      {/* Additional pathway lines */}
      <path
        d="M150 280 Q180 260 200 280 Q220 300 250 290"
        stroke="#1a1a1a"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />
      
      {/* Direction indicator */}
      <path
        d="M320 160 Q340 180 360 200 Q380 220 350 260 Q320 300 280 320"
        stroke="#1a1a1a"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      
      {/* Inner spiral */}
      <path
        d="M200 200 Q230 170 260 200 Q290 230 260 260 Q230 290 200 260 Q170 230 200 200"
        stroke="#1a1a1a"
        strokeWidth="3"
        fill="none"
      />
      
      {/* Curly decorative element */}
      <path
        d="M340 180 C360 160 380 180 370 200 C360 220 340 220 350 240 C360 260 340 280 320 270"
        stroke="#1a1a1a"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      
      {/* Small accent dots */}
      <circle cx="150" cy="280" r="6" fill="#7C3AED" />
      <circle cx="250" cy="290" r="4" fill="#1a1a1a" />
    </svg>
  )
}
