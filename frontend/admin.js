async function checkAuth() {
  try {
    const res = await fetch("/api/check-auth");
    if (!res.ok) {
      window.location.href = "/login.html";
    }
  } catch (error) {
    console.error("Ошибка авторизации", error);
    window.location.href = "/login.html";
  }
}

document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const resultDiv = document.getElementById("uploadResult");

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      resultDiv.textContent = "Ошибка при загрузке. Проверьте формат и содержимое файла.";
      resultDiv.style.color = "red";
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "output_stats.xlsx";
    link.click();
    URL.revokeObjectURL(url);

    resultDiv.textContent = "Файл успешно обработан и загружен.";
    resultDiv.style.color = "green";
  } catch (err) {
    console.error("Ошибка обработки файла:", err);
    resultDiv.textContent = "Не удалось обработать файл. Попробуйте снова.";
    resultDiv.style.color = "red";
  }
});

checkAuth();
