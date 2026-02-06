## Wendy Contreras Martinez – Light/Dark Mode Improvements 
## AI Tool Used

For this experiment, I used Gemini to help improve the light/dark mode implementation in our React app. The goal was to fix a styling issue where dark mode did not cover the entire screen and to make the theme toggle look and feel better.

## What Was Built / Produced

The first change fixed an issue where the background color only changed inside the React container instead of the whole page. The solution was to move the data-theme attribute to the HTML <body> using a useEffect hook, so the theme applies to the entire browser window.

The second change was replacing a basic checkbox with a custom toggle switch. The toggle changes between a day and night look using CSS variables, and includes sun and moon icons that fade in and out depending on the selected theme. The animation and movement of the switch were also improved to feel smoother.

## Reflection

### Usefulness of the AI Tool

The AI was helpful for quickly generating ideas and implementation details, especially for the CSS animations and transitions. Writing the toggle animation and timing functions by hand would have taken longer, and the AI gave a solid starting point that I could adjust afterward. It was most useful for speeding up UI experimentation rather than producing final code right away.

### Ensuring Correctness, Understanding, and Fair Use

The output still needed to be checked carefully. I made sure the data-theme attribute matched the CSS selectors and variables defined in :root, otherwise the theme would not update correctly. I also verified that the SVG icons were imported or defined inline properly to avoid dependency issues. After generating the code, I tested the theme switching manually to make sure everything worked consistently across the page. The AI output worked as a starting point, but changes were still needed to make it fit our project correctly.
