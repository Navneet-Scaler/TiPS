import {
  HomeIcon,
  PulseIcon,
  ClockIcon,
  StarIcon,
  TrendIcon,
  BrainIcon,
  FlaskIcon,
  BriefcaseIcon,
  TrophyIcon,
  CoinIcon,
  PeopleIcon,
  RocketIcon,
  MegaphoneIcon,
  MedalIcon,
  ToolIcon,
  BeakerIcon,
  CalendarIcon,
  TimelineIcon,
  LayersIcon,
} from "@/icons/Icons";

export type NavItem = {
  key: string;
  label: string;
  icon: typeof HomeIcon;
  category?: string;
};

export const NAV_SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: "Radar",
    items: [
      { key: "home", label: "Home", icon: HomeIcon },
      { key: "new", label: "New Today", icon: PulseIcon },
      { key: "closing", label: "Closing Soon", icon: ClockIcon },
      { key: "recommended", label: "Recommended", icon: StarIcon },
      { key: "trending", label: "Trending", icon: TrendIcon },
    ],
  },
  {
    title: "Ecosystem",
    items: [
      { key: "learning", label: "Learning", icon: BrainIcon, category: "Learning" },
      { key: "research", label: "Research", icon: FlaskIcon, category: "Research" },
      { key: "career", label: "Career", icon: BriefcaseIcon, category: "Career" },
      { key: "competitions", label: "Competitions", icon: TrophyIcon, category: "Competitions" },
      { key: "funding", label: "Funding", icon: CoinIcon, category: "Funding" },
      { key: "community", label: "Community", icon: PeopleIcon, category: "Community" },
      { key: "startup", label: "Startup", icon: RocketIcon, category: "Startup" },
      { key: "publishing", label: "Publishing", icon: MegaphoneIcon, category: "Publishing" },
      { key: "oss", label: "Open Source", icon: ToolIcon, category: "Open Source" },
      { key: "beta", label: "Beta Programs", icon: BeakerIcon, category: "Beta Programs" },
      { key: "recognition", label: "Recognition", icon: MedalIcon, category: "Recognition" },
      { key: "resources", label: "Resources", icon: LayersIcon, category: "Resources" },
    ],
  },
  {
    title: "Views",
    items: [
      { key: "timeline", label: "Timeline", icon: TimelineIcon },
      { key: "calendar", label: "Calendar", icon: CalendarIcon },
    ],
  },
];

export const ALL_NAV_ITEMS = NAV_SECTIONS.flatMap((s) => s.items);

export const CATEGORY_COLORS: Record<string, string> = {
  Learning: "#5b8cff",
  Research: "#7ad0ff",
  Career: "#ffb454",
  Competitions: "#ff7ab3",
  Funding: "#6fe2a8",
  "Open Source": "#c58bff",
  Community: "#ffd166",
  Startup: "#ff8a5b",
  Publishing: "#5be0d0",
  "Beta Programs": "#a3e635",
  Recognition: "#f472b6",
  Resources: "#94a3b8",
};

export function colorForCategory(category: string): string {
  return CATEGORY_COLORS[category] ?? "#5b8cff";
}
