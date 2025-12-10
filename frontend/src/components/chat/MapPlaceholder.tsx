import { MapPin } from "lucide-react";

const MapPlaceholder = () => {
  return (
    <div className="mt-3 rounded-md border border-border bg-muted/30 flex flex-col items-center justify-center py-12 px-6">
      <MapPin className="h-8 w-8 text-muted-foreground mb-3" />
      <p className="text-sm text-muted-foreground">Map coming soon…</p>
    </div>
  );
};

export default MapPlaceholder;
