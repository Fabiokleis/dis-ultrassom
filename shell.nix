let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
 
  nativeBuildInputs = with pkgs; [
  	doctest
		cmake
		pkg-config
		uv
		python312
	];
  buildInputs = with pkgs; [ armadillo openblas ];
  	      
  env = {
    UV_LINK_MODE = "copy"; 
    
    UV_PYTHON = "${pkgs.python312}/bin/python3"; 
    
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
    ];
  };
}
