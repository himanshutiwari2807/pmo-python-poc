import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#1B2A4A",
        cyan: "#009EC2",
        orange: "#F58426",
        oer: "#6EE7C0",
      },
    },
  },
  plugins: [],
} satisfies Config;
