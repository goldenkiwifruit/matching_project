document.addEventListener("DOMContentLoaded", () => {
  const mainImg = document.getElementById("mainImage");
  const thumbs = document.querySelectorAll(".thumb");

  thumbs.forEach(thumb => {
    thumb.addEventListener("click", () => {
      // 現在のメイン画像
      const currentMainSrc = mainImg.src;

      // 押したサムネの画像
      const clickedSrc = thumb.src;

      // 入れ替え
      mainImg.src = clickedSrc;
      thumb.src = currentMainSrc;
    });
  });
});
