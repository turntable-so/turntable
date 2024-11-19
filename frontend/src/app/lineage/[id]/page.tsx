import { LineageView } from "../../contexts/LineageView";

export default async function LineagePage() {
  return (
    <div className="w-full h-screen overflow-y-scroll">
      <LineageView />
    </div>
  );
}
