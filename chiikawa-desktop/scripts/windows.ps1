$ErrorActionPreference = 'Stop'
Add-Type @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class DesktopWindows {
 [StructLayout(LayoutKind.Sequential)] public struct R {public int Left,Top,Right,Bottom;}
 public delegate bool Callback(IntPtr h,IntPtr p);
 [DllImport("user32.dll")] static extern bool EnumWindows(Callback cb,IntPtr p);
 [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] static extern bool IsIconic(IntPtr h);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
 [DllImport("user32.dll")] static extern int GetWindowTextLength(IntPtr h);
 [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] static extern IntPtr SetThreadDpiAwarenessContext(IntPtr c);
 [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h,int a,out R r,int size);
 [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h,int a,out int v,int size);
 public class W {public string id;public int x,y,width,height; public bool foreground;}
 public static List<W> Read(int own) {
  SetThreadDpiAwarenessContext(new IntPtr(-4));
  var list=new List<W>(); var fg=GetForegroundWindow();
  EnumWindows((h,p)=>{uint pid;GetWindowThreadProcessId(h,out pid);int cloaked;R r;
   if(pid==own || !IsWindowVisible(h)||IsIconic(h)||GetWindowTextLength(h)==0)return true;
   if(DwmGetWindowAttribute(h,14,out cloaked,4)==0&&cloaked!=0)return true;
   if(DwmGetWindowAttribute(h,9,out r,16)!=0)return true;
   if(r.Right-r.Left<120||r.Bottom-r.Top<80)return true;
   list.Add(new W{id=h.ToString(),x=r.Left,y=r.Top,width=r.Right-r.Left,height=r.Bottom-r.Top,foreground=h==fg});return true;
  },IntPtr.Zero);return list;
 }
}
'@
while ($true) {
 $items=[DesktopWindows]::Read([int]$args[0])
 ConvertTo-Json -InputObject @($items.ToArray()) -Compress
 Start-Sleep -Milliseconds 300
}
