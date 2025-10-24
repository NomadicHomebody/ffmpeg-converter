# Use the NVIDIA CUDA development image as the base. It includes the full toolkit.
FROM nvidia/cuda:13.0.0-devel-ubuntu22.04

# Set environment variables for non-interactive installation
# ENV DEBIAN_FRONTEND=noninteractive
# ENV PYTHONUNBUFFERED 1
# ENV PATH=/usr/local/cuda/bin:$PATH
# ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:${PKG_CONFIG_PATH}

# Install necessary build tools and dependencies for FFmpeg and NVIDIA codecs
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    nasm \
    yasm \
    git \
    libssl-dev \
    libx264-dev \
    libx265-dev \
    libvpx-dev \
    libfdk-aac-dev \
    libmp3lame-dev \
    libopus-dev \
    libva-dev \
    libvdpau-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Clone nv-codec-headers for NVIDIA hardware acceleration
RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git /usr/src/nv-codec-headers && \
    cd /usr/src/nv-codec-headers && \
    make install

# Download and compile FFmpeg
ARG FFMPEG_VERSION="8.0" # Or your desired FFmpeg version
RUN git clone https://git.ffmpeg.org/ffmpeg.git /usr/src/ffmpeg && \
    cd /usr/src/ffmpeg && \
    git checkout n${FFMPEG_VERSION} && \
    ./configure \
    --enable-gpl \
    --enable-nonfree \
    --enable-cuda-nvcc \
    --enable-libnpp \
    --enable-libsvtav1 \
    --enable-libaom \
    --enable-nvenc \
    --enable-nvdec \
    --extra-cflags="-I/usr/local/cuda/include/" \
    --extra-ldflags="-L/usr/local/cuda/lib64/" \
    --bindir="/usr/local/bin" \
    --enable-ffnvcodec \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libvpx \
    --enable-libfdk-aac \
    --enable-libmp3lame \
    --enable-libopus && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# Set environment variables for NVIDIA driver capabilities
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,video

# --- Application Setup ---
WORKDIR /app

# Copy application code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]