import * as React from "react";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "secondary";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "default", size = "default", ...props }, ref) => {
    let baseClass = "inline-flex items-center justify-center rounded-xl font-bold transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 active:scale-95";
    
    if (variant === "default") baseClass += " bg-blue-600 text-white shadow-md hover:bg-blue-700 active:bg-blue-800";
    if (variant === "outline") baseClass += " border border-slate-300 bg-white text-slate-700 hover:bg-slate-50";
    if (variant === "ghost") baseClass += " text-slate-600 hover:bg-slate-100";
    if (variant === "secondary") baseClass += " bg-slate-100 text-slate-900 hover:bg-slate-200";

    if (size === "sm") baseClass += " h-9 px-3 text-xs";
    if (size === "default") baseClass += " h-11 px-5 text-sm";
    if (size === "lg") baseClass += " h-14 px-8 text-base";
    if (size === "icon") baseClass += " h-10 w-10";

    return (
      <button
        className={`${baseClass} ${className}`}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
