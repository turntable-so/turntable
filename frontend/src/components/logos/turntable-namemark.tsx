import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

const width = 315 / 2.5;
const height = 54 / 2.5;

const NameMark = () => {
  const [mounted, setMounted] = useState(false);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null; // Prevent flash of wrong theme

  // Only access resolvedTheme after mounting to avoid hydration mismatch
  const fillColor = resolvedTheme === "dark" ? "#ffffff" : "#1D1D1D";

  return (
    <svg
      aria-label="Turntable Namemark"
      width={width}
      height={height}
      viewBox="0 0 315 54"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>Turntable Namemark</title>
      <path
        d="M297.405 53.8019C286.542 53.8019 278.45 45.9286 278.45 34.9205C278.45 24.6414 285.813 16.2578 296.53 16.2578C307.319 16.2578 314.026 24.0582 314.026 34.0457V36.9617H285.449C286.251 43.0854 290.916 47.3866 297.332 47.3866C301.706 47.3866 305.642 45.4912 307.756 41.5545L313.297 44.3977C310.162 50.5214 304.403 53.8019 297.405 53.8019ZM285.74 32.2961H306.809C306.517 26.6098 302.362 22.746 296.457 22.746C290.406 22.746 286.469 26.9743 285.74 32.2961Z"
        fill={fillColor}
      />
      <path
        d="M264.652 0.875488H271.87V52.9998H264.652V0.875488Z"
        fill={fillColor}
      />
      <path
        d="M239.005 53.8746C228.215 53.8746 219.978 45.7826 219.978 35.2119V0.875488H227.195V21.7252C230.111 18.5176 234.485 16.4034 239.296 16.4034C250.159 16.4034 257.959 24.3497 257.959 35.2119C257.959 45.491 249.794 53.8746 239.005 53.8746ZM239.005 47.0948C245.639 47.0948 250.742 41.7001 250.742 35.139C250.742 28.6508 245.639 23.2561 239.005 23.2561C232.298 23.2561 227.195 28.6508 227.195 35.139C227.195 41.7001 232.298 47.0948 239.005 47.0948Z"
        fill={fillColor}
      />
      <path
        d="M192.435 53.8745C182.083 53.8745 174.501 45.418 174.501 35.066C174.501 24.8599 182.666 16.4033 193.528 16.4033C204.318 16.4033 212.555 24.4225 212.555 35.066V52.9997H205.703V46.7302C203.005 51.1043 198.267 53.8745 192.435 53.8745ZM193.528 47.0218C200.235 47.0218 205.338 41.6271 205.338 35.1389C205.338 28.5778 200.235 23.1831 193.528 23.1831C186.894 23.1831 181.718 28.5778 181.718 35.1389C181.718 41.6271 186.894 47.0218 193.528 47.0218Z"
        fill={fillColor}
      />
      <path
        d="M163.826 53.9473C154.932 53.9473 150.193 48.3339 150.193 40.1689V23.5475H143.122V17.278H150.193V8.01953H157.411V17.278H171.116V23.5475H157.411V39.9502C157.411 44.6159 160.181 47.3862 164.482 47.3862C166.815 47.3862 169.366 46.5113 171.116 45.272V51.906C169.294 53.1453 166.45 53.9473 163.826 53.9473Z"
        fill={fillColor}
      />
      <path
        d="M122.139 23.3289C115.14 23.3289 111.641 29.0881 111.641 35.7221V52.9997H104.424V34.9931C104.424 24.5683 110.62 16.4033 122.139 16.4033C133.803 16.4033 140.145 24.5683 140.145 34.9202V52.9997H132.928V35.795C132.928 29.0881 129.283 23.3289 122.139 23.3289Z"
        fill={fillColor}
      />
      <path
        d="M88.9272 52.9999H81.71V31.7128C81.71 23.0375 86.6672 16.5493 95.9986 16.5493C98.2585 16.5493 100.591 16.9867 102.414 17.8615V25.0059C100.664 23.9852 98.623 23.4749 96.6547 23.4749C91.8432 23.4749 88.9272 26.7555 88.9272 32.0044V52.9999Z"
        fill={fillColor}
      />
      <path
        d="M57.0477 46.8762C63.6818 46.8762 67.3268 41.117 67.3268 34.483V17.2783H74.544V35.3578C74.544 45.7098 68.2745 53.8747 57.0477 53.8747C45.9668 53.8747 39.6973 45.6369 39.6973 35.2849V17.2783H46.9145V34.5559C46.9145 41.117 50.4866 46.8762 57.0477 46.8762Z"
        fill={fillColor}
      />
      <path
        d="M37.4188 4.15625V11.009H22.4012V53H14.9652V11.009H0.0205078V4.15625H37.4188Z"
        fill={fillColor}
      />
    </svg>
  );
};

export default NameMark;
