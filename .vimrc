filetype plugin indent on                   " detect file plugin+indent
syntax on                                   " syntax highlighting

set cursorline                              " hilight cursor line
set cursorcolumn
set more                                    " ---more--- like less
set number                                  " line numbers
set scrolloff=3                             " lines above/below cursor
set showcmd                                 " show cmds being typed
set title                                   " window title
set vb t_vb=                                " disable beep and flashing
set wildmenu                                " better auto complete
set wildmode=longest,list                   " bash-like auto complete
set hidden                                  " buffer change, more undo
set history=1000                            " default 20
set iskeyword+=_,$,@,%,#                    " not word dividers
set laststatus=2                            " always show statusline
set linebreak                               " don't cut words on wrap
set listchars=tab:>\                        " > to highlight <tab>
set list                                    " displaying listchars
set mouse=                                  " disable mouse
set noshowmode                              " hide mode, got powerline
set noexrc                                  " don't use other .*rc(s)
set nostartofline                           " keep cursor column pos
set nowrap                                  " don't wrap lines
set numberwidth=5                           " 99999 lines
set shortmess+=I                            " disable startup message
set splitbelow                              " splits go below w/focus
set splitright                              " vsplits go right w/focus
set autoread                                " refresh if changed
set backup                                  " backup curr file
set confirm                                 " confirm changed files
set noautowrite                             " never autowrite
set updatecount=50                          " update swp after 50chars
set autoindent                              " preserve indentation
set backspace=indent,eol,start              " smart backspace
set cinkeys-=0#                             " don't force # indentation
set expandtab                               " no real tabs
set nrformats+=alpha                        " incr/decr letters C-a/-x
set shiftround                              " be clever with tabs
set shiftwidth=4                            " default 8
set smartcase                               " igncase,except capitals
set smarttab                                " tab to 0,4,8 etc.
set softtabstop=4                           " "tab" feels like <tab>
set tabstop=4                               " replace <TAB> w/4 spaces
""" Persistent undo. Requires Vim 7.3 {{{
    if has('persistent_undo') && exists("&undodir")
        set undodir=$HOME/.vim/undo/            " where to store undofiles
        set undofile                            " enable undofile
        set undolevels=500                      " max undos stored
        set undoreload=10000                    " buffer stored undos
    endif
""" }}}

set t_Co=256                                " 256-colors
colors jellybeans                           " select colorscheme
let g:jellybeans_overrides = {
\    'background': { '256ctermbg': 'none' },
\}
set background=dark                         " we're using a dark bg

let mapleader=","
map <leader>.     <Plug>NERDCommenterToggle
