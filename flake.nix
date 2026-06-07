{
  description = "Ambiente de desenvolvimento para o Desafio Lacrei Saúde";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pkgs.python312
            pkgs.poetry
            pkgs.docker
            pkgs.docker-compose
            pkgs.postgresql_16
          ];

          # Força o Poetry a usar o Python do Nix via variáveis de ambiente
          env = {
            POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON = "true";
            POETRY_VIRTUALENVS_IN_PROJECT = "true";
            POETRY_VIRTUALENVS_CREATE = "true";
          };

          shellHook = ''
            # Força o Poetry a usar o interpretador Python 3.12 do Nix
            poetry env use $(which python3) > /dev/null 2>&1

            echo "🚀 Nix + Poetry Environment Active"
            echo "🐍 Python: $(python3 --version)"
            echo "📦 Poetry: $(poetry --version)"
            echo "✨ Virtualenv: $(poetry env info -p 2>/dev/null || echo 'Not initialized')"
          '';
        };
      });
}
