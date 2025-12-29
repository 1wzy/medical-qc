/**
 * 路由路径到图标的映射
 */
export const routeIconMap: Record<string, string> = {
  '/dashboard': 'Monitor',
  '/rule/manage': 'Setting',
  '/rule/set': 'List',
  '/data/basic': 'Folder',
  '/data/dataset': 'Files',
  '/batches': 'Files',
  '/api-test': 'Tools',
}

/**
 * 根据路径获取图标
 */
export function getRouteIcon(path: string): string | undefined {
  // 精确匹配
  if (routeIconMap[path]) {
    return routeIconMap[path]
  }
  
  // 前缀匹配（用于动态路由）
  for (const [routePath, icon] of Object.entries(routeIconMap)) {
    if (path.startsWith(routePath)) {
      return icon
    }
  }
  
  return undefined
}

