<template>
  <router-view></router-view>
</template>

<style>
/* 清除浏览器默认的内外边距 */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  /* 将背景底色统一刷成浅灰，避免边缘有白边 */
  background-color: #f0f2f5;
}

/* 让 Vue 的挂载根节点也 100% 撑满 */
#app {
  width: 100%;
  height: 100%;
  max-width: none !important; /* 强行覆盖可能遗留的 max-width */
  padding: 0 !important;      /* 强行覆盖可能遗留的 padding */
}
</style>