import ObsidianWorkbench from "./obsidian-workbench";
import initialData from "../public/navigation-fallback.json";

export default function Home() {
  return <ObsidianWorkbench initialData={initialData as any} />;
}
