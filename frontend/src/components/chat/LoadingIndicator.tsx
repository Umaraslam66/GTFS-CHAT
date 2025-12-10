const LoadingIndicator = () => {
  return (
    <div className="flex items-center gap-1 px-4 py-3" aria-label="Loading">
      <span className="loading-dot w-2 h-2 rounded-full bg-muted-foreground" />
      <span className="loading-dot w-2 h-2 rounded-full bg-muted-foreground" />
      <span className="loading-dot w-2 h-2 rounded-full bg-muted-foreground" />
    </div>
  );
};

export default LoadingIndicator;
