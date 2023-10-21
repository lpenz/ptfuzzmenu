{
  description =
    ''
      Fuzzy-filtering menu widget for prompt-toolkit
    '';
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages."${system}";
        ptfuzzmenu = pkgs.python3Packages.buildPythonApplication {
          pname = "ptfuzzmenu";
          version = "0.1.0";
          src = self;
        };
      in
      rec {
        packages.default = ptfuzzmenu;
      }
    );
}
