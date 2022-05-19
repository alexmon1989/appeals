import {fileURLToPath, URL} from 'url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

const { resolve } = require('path');

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    root: resolve('./frontend'),
    base: '/static/',
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./frontend', import.meta.url)),
            vue: 'vue/dist/vue.esm-bundler.js',
        }
    },
    build: {
        outDir: resolve('./frontend/dist/app'),
        manifest: true,
        assetsDir: '',
        rollupOptions: {
            input: {
                main: resolve('./frontend/app/main.js'),
            },
            output: {
                chunkFileNames: undefined,
            },
        },
    }
})
