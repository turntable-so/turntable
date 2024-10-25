export default function TextInput({
  value,
  size,
}: { value: string; size: string }) {
  return (
    <input
      className={`border-transparent focus:outline-none focus:border-transparent focus:ring-0 scroll-m-20 ${size} bg-transparent font-medium tracking-tight`}
      value={value}
    />
  );
}
