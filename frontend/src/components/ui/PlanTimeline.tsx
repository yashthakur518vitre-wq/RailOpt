import React from 'react';

export default function PlanTimeline({ blocks = [], horizon_days = 7, reference_start }: { blocks: any[], horizon_days: number, reference_start?: string }) {
  if (!blocks || blocks.length === 0) {
    return <div className="p-8 text-center text-slate-500">No blocks to display</div>;
  }

  // Group blocks by corridor
  const corridors = Array.from(new Set(blocks.map(b => b.corridor_id))).sort();
  
  // Find min and max time to set the timeline boundaries
  const allStarts = blocks.map(b => new Date(b.start_time).getTime());
  // Use actual planning horizon start instead of first scheduled block
  const minTime = reference_start ? new Date(reference_start).getTime() : Math.min(...allStarts);
  
  // Force the timeline to show exactly the horizon length from the first block
  const totalDurationMs = horizon_days * 24 * 60 * 60 * 1000; 

  const getLeftPercentage = (time: string) => {
    const t = new Date(time).getTime();
    return Math.max(0, ((t - minTime) / totalDurationMs) * 100);
  };

  const getWidthPercentage = (start: string, end: string) => {
    const s = new Date(start).getTime();
    const e = new Date(end).getTime();
    return Math.max(0.5, ((e - s) / totalDurationMs) * 100);
  };

  const formatTick = (dayOffset: number) => {
    const d = new Date(minTime + dayOffset * 24 * 60 * 60 * 1000);
    return d.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const days = Array.from({ length: horizon_days }, (_, i) => i);

  return (
    <div className="w-full overflow-x-auto pb-4">
      <div className="min-w-[800px]">
        {/* Timeline Header (Days) */}
        <div className="flex border-b border-slate-200 dark:border-ink-track ml-32 relative h-8">
          {days.map(day => (
            <div key={day} className="absolute text-xs text-slate-500 font-medium" style={{ left: `${(day / horizon_days) * 100}%` }}>
              <div className="pl-2 pt-1 border-l h-8 border-slate-200 dark:border-ink-track">
                {formatTick(day)}
              </div>
            </div>
          ))}
        </div>

        {/* Corridors and Blocks */}
        <div className="space-y-2 mt-4">
          {corridors.map(corridor_id => {
            const corridorBlocks = blocks.filter(b => b.corridor_id === corridor_id);
            return (
              <div key={corridor_id} className="flex relative items-center group">
                
                {/* Corridor Label */}
                <div className="w-32 shrink-0 pr-4 text-right">
                  <span className="font-bold text-sm text-slate-700 dark:text-slate-300 font-data">{String(corridor_id)}</span>
                </div>
                
                {/* Track Lane */}
                <div className="flex-1 h-12 bg-ink-track/5 dark:bg-ink-track/40 rounded-sm relative border-y border-slate-200 dark:border-slate-800 overflow-hidden shadow-inner">
                  
                  {/* Grid Lines */}
                  {days.map(day => (
                    <div key={`grid-${day}`} className="absolute top-0 bottom-0 border-l border-slate-200 dark:border-slate-700 opacity-20 pointer-events-none" style={{ left: `${(day / horizon_days) * 100}%` }} />
                  ))}
                  
                  {/* Hatched Occupancy Strip - Optional placeholder if train_occupancy data is ever sent */}
                  {/* <div className="absolute inset-0 bg-signal-red/40" style={{ backgroundImage: "repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.1) 10px, rgba(255,255,255,0.1) 20px)", display: hasOccupancy ? 'block' : 'none' }}></div> */}

                  {/* Render Blocks */}
                  {corridorBlocks.map(block => {
                    const left = getLeftPercentage(block.start_time);
                    const width = getWidthPercentage(block.start_time, block.end_time);
                    const isCoordinated = block.coordinated;
                    
                    return (
                      <div 
                        key={block.block_id}
                        onClick={() => {
                          const row = document.getElementById(`task-${block.tasks?.[0]}`);
                          if (row) {
                            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            row.classList.add('bg-blue-50', 'dark:bg-blue-900/20');
                            setTimeout(() => row.classList.remove('bg-blue-50', 'dark:bg-blue-900/20'), 2000);
                          }
                        }}
                        className={`absolute top-1.5 bottom-1.5 rounded-sm shadow-md border overflow-hidden cursor-pointer transition-all hover:z-10 hover:shadow-lg ${
                          isCoordinated 
                            ? 'bg-steel border-steel-dark text-white' 
                            : 'bg-signal-green border-signal-green text-ink'
                        }`}
                        style={{ left: `${left}%`, width: `${width}%` }}
                        title={`${block.block_id}\nTasks: ${block.tasks?.join(', ')}\nDept: ${block.department}\nTime: ${new Date(block.start_time).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})} - ${new Date(block.end_time).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}`}
                      >
                        <div className={`h-full w-full flex items-center justify-center text-[10px] font-bold font-data`}>
                          {width > 2 && (isCoordinated ? 'COORD' : block.tasks?.length > 1 ? 'M' : '1')}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  );
}
