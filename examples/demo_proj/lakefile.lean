import Lake
open Lake DSL

package «demo_proj» where
  -- Settings applied to both builds and interactive editing
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩ -- pretty-prints `fun a ↦ b`
  ]
  -- add any additional package configuration options here

def leanVersion : String := s!"v{Lean.versionString}"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ leanVersion

@[default_target]
lean_lib «DemoProj» where
  -- add any library configuration options here
