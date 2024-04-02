:set number
:set relativenumber
:set autoindent
:set tabstop=4
:set shiftwidth=4
:set smarttab
:set softtabstop=4
:set mouse=a

call plug#begin()
Plug 'dracula/vim', { 'as': 'dracula' }
Plug 'https://github.com/vim-airline/vim-airline'
Plug 'https://github.com/preservim/tagbar'
Plug 'https://github.com/ryanoasis/vim-devicons'
Plug 'https://github.com/neovim/nvim-lspconfig'
Plug 'https://github.com/hrsh7th/nvim-cmp'
Plug 'https://github.com/nvim-lua/plenary.nvim'
Plug 'https://github.com/nvim-telescope/telescope.nvim'
Plug 'https://github.com/kylechui/nvim-surround'
Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'jiangmiao/auto-pairs'
Plug 'tmhedberg/matchit'
Plug 'tpope/vim-fugitive'



call plug#end()
colorscheme dracula

" Set the background color with 80% opacity
hi Normal guibg=#282a36 ctermbg=NONE
hi NonText guibg=#282a36 ctermbg=NONE
hi VertSplit guibg=#282a36 ctermbg=NONE
hi StatusLine guibg=#282a36 ctermbg=NONE
hi StatusLineNC guibg=#282a36 ctermbg=NONE
hi StatusLineTerm guibg=#282a36 ctermbg=NONE
hi StatusLineTermNC guibg=#282a36 ctermbg=NONE
hi LineNr guibg=#282a36 ctermbg=NONE
hi SignColumn guibg=#282a36 ctermbg=NONE
hi NormalNC guibg=#282a36 ctermbg=NONE

" Disable background highlight for search results
set nohlsearch
" For Vimscript configuration
inoremap <expr> <CR> coc#pum#visible() ? coc#pum#confirm() : "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

