FROM astrocrpublic.azurecr.io/runtime:3.1-7


# Switch to root to install OS packages if needed
USER root

# Install extra OS-level dependencies (optional)
# For PDF parsing, poppler isn't required for PyPDF2. Leaving here for future use.
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to astro user before installing python libs
USER astro

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt