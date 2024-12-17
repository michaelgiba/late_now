# Late Now! 🎭📺

An experiment into controllable short-form show generation. For detailed information visit the [Technical Overview](https://michaelgiba.substack.com/p/late-now)

## 🚀 Usage

There are two available execution modes:

1. **Show from News Article**: 
   ```
   ./bin/show-from-article <url of article>
   ```

2. **Show from rough script**:
   ```
   ./bin/show-from-script <path to script>
   ```

The content of a script file is just a plain text file that looks like a script. For some examples, look into `show_scripts/`


## 🛠️ Getting Started

### Prerequisites

- [Blender 4.2](https://www.blender.org/download/releases/4-2/) with [Autorig Pro](https://blendermarket.com/products/auto-rig-pro) installed
- Python 3.10
- GPU with at least 12 GB of VRAM (Tested on GeForce RTX 3060)


### Setup

1. Clone the repo
2. Run `./setup.sh`
3. Download the pretrained models in each of the cloned AniPortrait and MoMask repos
4. Fill out the settings in `settings.env`

## 🎬 Example Generations

### From Script

```
*Shows an image of a smiling emoji*

(Applause)
Walter: Hey there! (Waving)
(Oooh)
Walter: Signing off (Salutes)
(Awww)
```

**Video**: 

https://github.com/user-attachments/assets/1c5a6e94-6214-48f1-87c0-d212f7c5f9ae


### From Article

**Article link**: [Quanta - Even a Single Bacterial Cell Can Sense the Seasons Changing](https://www.quantamagazine.org/even-a-single-bacterial-cell-can-sense-the-seasons-changing-20241011/)

**Video**: 

https://github.com/user-attachments/assets/c18bb13a-0a60-438d-aedd-aaa76a9a8a6a


## 📜 License

Apache 2.0

## 🤝 Contributing

All contributions are welcome! Some potential extensions include:

- Optimize end-to-end generation time using distributed computing
- Deploy as a web service for video generation
- Create a continuous show similar to "Nothing Forever"
- Integrate 3D generation models for new characters/scenes
- Add img2img processing for frame styling

Feel free to fork the repository and contribute your own ideas!
