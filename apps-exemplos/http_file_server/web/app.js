const state = {
  files: [],
  maxUploadBytes: 0,
};

const elements = {
  fileList: document.querySelector("#fileList"),
  emptyState: document.querySelector("#emptyState"),
  fileCount: document.querySelector("#fileCount"),
  searchInput: document.querySelector("#searchInput"),
  fileInput: document.querySelector("#fileInput"),
  chooseFiles: document.querySelector("#chooseFiles"),
  dropZone: document.querySelector("#dropZone"),
  progressArea: document.querySelector("#progressArea"),
  uploadLimit: document.querySelector("#uploadLimit"),
  toastContainer: document.querySelector("#toastContainer"),
};

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, index)).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatDate(isoString) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(isoString));
}

function extensionLabel(name) {
  const dot = name.lastIndexOf(".");
  if (dot <= 0 || dot === name.length - 1) return "FILE";
  return name.slice(dot + 1).toUpperCase().slice(0, 5);
}

function showToast(message, type = "default") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 3600);
}

async function api(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;
  if (!response.ok) {
    throw new Error(body?.error || `Erro HTTP ${response.status}`);
  }
  return body;
}

async function loadFiles() {
  try {
    const data = await api("/api/files");
    state.files = data.files;
    state.maxUploadBytes = data.max_upload_bytes;
    elements.fileCount.textContent = data.count;
    elements.uploadLimit.textContent = `Limite de ${formatBytes(state.maxUploadBytes)} por arquivo`;
    renderFiles();
  } catch (error) {
    showToast(`Falha ao carregar os arquivos: ${error.message}`, "error");
  }
}

function renderFiles() {
  const query = elements.searchInput.value.trim().toLowerCase();
  const filtered = state.files.filter((file) => file.name.toLowerCase().includes(query));

  elements.fileList.replaceChildren();
  elements.emptyState.hidden = filtered.length > 0;

  if (filtered.length === 0) {
    elements.emptyState.querySelector("h3").textContent = query ? "Nenhum resultado" : "Nenhum arquivo por aqui";
    elements.emptyState.querySelector("p").textContent = query
      ? "Tente outro termo de busca."
      : "Envie o primeiro arquivo usando a área acima.";
    return;
  }

  for (const file of filtered) {
    const row = document.createElement("article");
    row.className = "file-row";

    const main = document.createElement("div");
    main.className = "file-main";

    const icon = document.createElement("div");
    icon.className = "file-icon";
    icon.textContent = extensionLabel(file.name);

    const info = document.createElement("div");
    info.style.minWidth = "0";

    const name = document.createElement("div");
    name.className = "file-name";
    name.title = file.name;
    name.textContent = file.name;

    const meta = document.createElement("div");
    meta.className = "file-meta";
    meta.textContent = `${formatBytes(file.size)} • ${formatDate(file.modified)}`;

    info.append(name, meta);
    main.append(icon, info);

    const actions = document.createElement("div");
    actions.className = "file-actions";

    const download = document.createElement("button");
    download.className = "action-btn primary";
    download.type = "button";
    download.textContent = "Baixar";
    download.addEventListener("click", () => {
      window.location.href = file.download_url;
    });

    const remove = document.createElement("button");
    remove.className = "action-btn danger";
    remove.type = "button";
    remove.textContent = "Excluir";
    remove.addEventListener("click", () => deleteFile(file.name));

    actions.append(download, remove);
    row.append(main, actions);
    elements.fileList.appendChild(row);
  }
}

async function deleteFile(name) {
  if (!confirm(`Excluir “${name}”?`)) return;

  try {
    await api(`/api/files/${encodeURIComponent(name)}`, { method: "DELETE" });
    showToast("Arquivo excluído.", "success");
    await loadFiles();
  } catch (error) {
    showToast(`Não foi possível excluir: ${error.message}`, "error");
  }
}

function createProgress(file) {
  elements.progressArea.hidden = false;

  const item = document.createElement("div");
  item.className = "progress-item";

  const row = document.createElement("div");
  row.className = "progress-row";

  const label = document.createElement("span");
  label.textContent = file.name;

  const status = document.createElement("strong");
  status.textContent = "Enviando…";

  const track = document.createElement("div");
  track.className = "progress-track";

  const bar = document.createElement("div");
  bar.className = "progress-bar";

  row.append(label, status);
  track.appendChild(bar);
  item.append(row, track);
  elements.progressArea.appendChild(item);

  return { item, status, bar };
}

function uploadOne(file) {
  return new Promise((resolve, reject) => {
    if (state.maxUploadBytes && file.size > state.maxUploadBytes) {
      reject(new Error(`${file.name}: excede o limite de ${formatBytes(state.maxUploadBytes)}.`));
      return;
    }

    const progress = createProgress(file);
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", `/api/files/${encodeURIComponent(file.name)}`);
    xhr.setRequestHeader("Content-Type", file.type || "application/octet-stream");

    xhr.upload.addEventListener("progress", (event) => {
      if (!event.lengthComputable) return;
      const percent = Math.round((event.loaded / event.total) * 100);
      progress.bar.style.width = `${percent}%`;
      progress.status.textContent = `${percent}%`;
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        progress.bar.style.width = "100%";
        progress.status.textContent = "Concluído";
        setTimeout(() => {
          progress.item.remove();
          if (!elements.progressArea.children.length) elements.progressArea.hidden = true;
        }, 900);
        resolve();
      } else {
        let message = `Erro HTTP ${xhr.status}`;
        try { message = JSON.parse(xhr.responseText).error || message; } catch (_) {}
        progress.status.textContent = "Erro";
        reject(new Error(message));
      }
    });

    xhr.addEventListener("error", () => {
      progress.status.textContent = "Erro";
      reject(new Error("Falha de rede durante o upload."));
    });

    xhr.send(file);
  });
}

async function uploadFiles(fileList) {
  const files = Array.from(fileList);
  if (!files.length) return;

  for (const file of files) {
    try {
      await uploadOne(file);
      showToast(`${file.name} enviado com sucesso.`, "success");
    } catch (error) {
      showToast(error.message, "error");
    }
  }

  elements.fileInput.value = "";
  await loadFiles();
}

elements.chooseFiles.addEventListener("click", () => elements.fileInput.click());
elements.fileInput.addEventListener("change", (event) => uploadFiles(event.target.files));
elements.searchInput.addEventListener("input", renderFiles);

for (const eventName of ["dragenter", "dragover"]) {
  elements.dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropZone.classList.add("dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  elements.dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropZone.classList.remove("dragging");
  });
}

elements.dropZone.addEventListener("drop", (event) => {
  uploadFiles(event.dataTransfer.files);
});

loadFiles();
