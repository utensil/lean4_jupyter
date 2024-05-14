import Lake
open Lake DSL

def leanVersion : String := s!"v{Lean.versionString}"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ leanVersion

package «demo_proj» where
  -- add package configuration options here

lean_lib «DemoProj» where
  -- add library configuration options here

@[default_target]
lean_exe «demo_proj» where
  root := `Main
