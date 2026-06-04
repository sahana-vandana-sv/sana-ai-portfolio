interface AvatarStackProps {
  count?: number;
  extra?: number;
}

const FACES = ["🧑🏻", "🧑🏽", "🧑🏼", "👩🏻", "👨🏽"];
const BGS = ["bg-blush", "bg-butter", "bg-mint", "bg-lilacSoft", "bg-sky"];

export default function AvatarStack({ count = 3, extra = 5 }: AvatarStackProps) {
  return (
    <div className="flex items-center">
      <div className="flex -space-x-3">
        {Array.from({ length: count }).map((_, i) => (
          <div
            key={i}
            className={`flex h-9 w-9 items-center justify-center rounded-full ring-2 ring-white text-base ${BGS[i % BGS.length]}`}
          >
            {FACES[i % FACES.length]}
          </div>
        ))}
      </div>
      {extra > 0 && (
        <span className="ml-2 text-sm font-medium text-ink/60">+{extra}</span>
      )}
    </div>
  );
}
