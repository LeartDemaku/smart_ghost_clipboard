using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;
using System.Reflection;
using System.Runtime.InteropServices;

[assembly: AssemblyTitle("Smart Ghost Clipboard")]
[assembly: AssemblyDescription("AI-Powered Ghost Clipboard & Intelligent Text Transformer")]
[assembly: AssemblyCompany("Swisstech")]
[assembly: AssemblyProduct("Smart Ghost Clipboard")]
[assembly: AssemblyCopyright("Copyright © 2026 Swisstech")]
[assembly: AssemblyVersion("2.0.0.0")]
[assembly: AssemblyFileVersion("2.0.0.0")]

namespace SmartGhostClipboardLauncher
{
    static class Program
    {
        [DllImport("user32.dll")]
        private static extern bool SetProcessDPIAware();

        [STAThread]
        static void Main(string[] args)
        {
            try
            {
                try { SetProcessDPIAware(); } catch { }

                string baseDir = AppDomain.CurrentDomain.BaseDirectory;
                string mainScript = Path.Combine(baseDir, "main.py");

                if (!File.Exists(mainScript))
                {
                    MessageBox.Show(
                        "Nuk u gjet skedari 'main.py' në direktorinë:\n" + baseDir + "\n\nSigurohuni që 'SmartGhostClipboard.exe' të jetë brenda dosjes kryesore të projektit.",
                        "Smart Ghost Clipboard — Gabim",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error
                    );
                    return;
                }

                string venvPythonW = Path.Combine(baseDir, "venv", "Scripts", "pythonw.exe");
                string venvPython = Path.Combine(baseDir, "venv", "Scripts", "python.exe");

                string pythonExe = "";

                if (File.Exists(venvPythonW))
                {
                    pythonExe = venvPythonW;
                }
                else if (File.Exists(venvPython))
                {
                    pythonExe = venvPython;
                }
                else
                {
                    pythonExe = "pythonw.exe";
                }

                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = pythonExe;

                string formattedArgs = "\"" + mainScript + "\"";
                if (args != null && args.Length > 0)
                {
                    formattedArgs += " " + string.Join(" ", args);
                }
                psi.Arguments = formattedArgs;
                psi.WorkingDirectory = baseDir;
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                psi.WindowStyle = ProcessWindowStyle.Hidden;

                Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Gabim gjatë ekzekutimit të aplikacionit:\n\n" + ex.Message,
                    "Smart Ghost Clipboard — Gabim",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}
