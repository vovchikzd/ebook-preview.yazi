local skip_labels = {
  ["Publisher"] = true
  , ["Tags"] = true
  , ["Identifiers"] = true
  , ["Published"] = true
  , ["Series"] = true
  , ["Book Producer"] = true
  , ["Rights"] = true
  , ["Title sort"] = true
  , ["Rating"] = true
  , ["ABC"] = true
  , ["author_fullsort"] = true
  , ["ereader"] = true
  , ["title_fullsort"] = true
  , ["Words"] = true
  , ["Pages"] = true
  , ["mr_sort"] = true
  , ["jacket"] = true
  , ["Fixed"] = true
  , ["Grade"] = true
  , ["Identified"] = true
  , ["isbn_asin"] = true
  , ["isbn_isbn"] = true
  , ["isbn_isbnp"] = true
}

local M = {}

function M:peek()
  local image_height = 0

	if self:preload() == 1 then
    local cache = ya.file_cache(self)
    if cache and fs.cha(cache).length > 0 then
      image_height = ya.image_show(cache, self.area).h
    end
	end

  local output, code = Command("ebook-meta"):args({
    tostring(self.file.url)
  }):stdout(Command.PIPED):output()

  local lines = {}

  if output then
    local i = 0
    for str in output.stdout:gmatch("[^\n]*") do
      local label, value = str:match("(.*[^ ]) +: (.*)")
      local line
      if label then
        if not skip_labels[label] then
          if label == "Comments" then
            label = "Summary"
            value = string.gsub(value, '<[^>]+>', "")
            value = string.gsub(value, '&[a-z0-9]+;', ' ')
            value = string.gsub(value, '&#[0-9]+;', ' ')
            value = string.gsub(value, '&#[0-9a-f]+;', ' ')
          end
          if value ~= "" then
            line = ui.Line({
              ui.Span(label .. ": "):bold(),
              ui.Span(value)
            })
          end
        end
      end

      if line then
        if i >= self.skip then
          table.insert(lines, line)
        end
        local max_width = math.max(1, self.area.w - 3)
        i = i + math.max(1, math.ceil(line:width() / max_width))
      end
    end
  else
    local error = string.format("Spawn ebook-meta returns %s", code)
    table.insert(lines, ui.Line(error))
  end

  ya.preview_widgets(self, {
    ui.Paragraph(
      ui.Rect({
        x = self.area.x,
        y = self.area.y + image_height,
        w = self.area.w,
        h = self.area.h - image_height,
      }),
      lines
    ):wrap(ui.Paragraph.WRAP),
  })
end

function M:seek(units)
  local h = cx.active.current.hovered
	if h and h.url == self.file.url then
		local step = math.floor(units * self.area.h / 200)
		ya.manager_emit("peek", {
			math.max(0, cx.active.preview.skip + step),
			only_if = self.file.url,
		})
	end
end

function M:preload()
	local cache = ya.file_cache(self)
	if not cache or fs.cha(cache) then
		return 1
	end

	local size = math.min(PREVIEW.max_width, PREVIEW.max_height)

	local child, code = Command("get-ebook-cover"):args({
		tostring(self.file.url),
    tostring(cache),
    tostring(size)
	}):spawn()

	if not child then
		ya.err("spawn `get-ebook-cover` command returns " .. tostring(code))
		return 0
	end

	local status = child:wait()
	return status and status.success and 1 or 2
end

return M
