const path = require('path');
const uglifyJsPlugin = require('uglifyjs-webpack-plugin');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const libraryName = 'chat-widget';
const outputFile = `${libraryName}.min.js`;


module.exports = {
    entry: './src/index.js',
    output: {
        library: libraryName,
        libraryTarget: 'umd',
        libraryExport: 'default',
        path: path.resolve(__dirname, 'dist'),
        filename: outputFile,
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/preset-env'],
                        },
                    },
                ],
            },
            {
                test: /\.woff($|\?)|\.woff2($|\?)|\.ttf($|\?)|\.eot($|\?)|\.svg($|\?)/i,
                type: 'asset/resource',
                generator: {
                    filename: 'fonts/[name][ext][query]'
                }
            },
            {
                test: /\.s?css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        // Translate CSS into CommonJS modules
                        loader: 'css-loader',
                    },
                    {
                        // Run postcss actions
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: [
                                    function () {
                                        return [require('autoprefixer')];
                                    }
                                ],
                            },
                        },
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sassOptions: {
                                outputStyle: "compressed",
                            }
                        }
                    }
                ],
            },
            {
                test: /\.html$/,
                use: ["html-loader"]
            }
        ],
    },
    plugins: [
        new uglifyJsPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        }),
        new MiniCssExtractPlugin()
    ],
};