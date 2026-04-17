{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [ doctest cmake pkg-config ];
  buildInputs = with pkgs; [ armadillo openblas ];
}