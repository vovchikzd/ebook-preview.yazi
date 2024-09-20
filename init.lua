local M = {}

function M:peek()
  local image_height = 0 -- for later

  if self:preload() == 1 then
    local cache = ya.file_cache(self)
    if cache and fs.cha(cache).length > 0 then
      image_height = ya.image_show(cache, self.area).h
    end
  end


  local cmd = ""
  local output, err = Command(cmd)
    :args({
      cmd
      , "info"
      , tostring(self.file.url)
    })
    :stdout(Command.PIPED)
    :output()

end

function M:seek() end

function M:preload() end

return M
