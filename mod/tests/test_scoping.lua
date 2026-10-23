-- luajit mod/tests/test_scoping.lua  (every mod Lua file): no global read of a name the same file declares as a local.
-- A function that uses a local declared further down reads the (nil) global of that name instead: the BeamMP session's
-- test switch errored that way (remoteOwners) and roads.lua's prewarm after a level reload never ran (2026-10-22).
-- Inspects LuaJIT bytecode directly, including under the Python/Lupa runner.
local dir = (arg[0]:match('^(.*)[/\\]') or '.')
local T = dofile(dir .. '/testlib.lua')
local root = dir .. '/../beamng_earth/lua'

local files = BNGE_TEST_LUA_FILES or {}
if not BNGE_TEST_LUA_FILES then
  local win = package.config:sub(1, 1) == '\\'
  local cmd = win and ('dir /b /s "' .. root:gsub('/', '\\') .. '\\*.lua"')
    or ('find "' .. root .. '" -name "*.lua"')
  local p = assert(io.popen(cmd))
  for f in p:lines() do files[#files + 1] = f end
  p:close()
end
T.check(#files > 20, 'found the mod\'s Lua files: ' .. #files)

local util, bit = require('jit.util'), require('bit')
-- Derive the opcode from a known global read instead of pinning a LuaJIT opcode number.
local globalRead = bit.band(util.funcbc(function() return BNGE_TEST_OPCODE_PROBE end, 1), 255)
local function globalReads(fn, seen)
  local info = util.funcinfo(fn)
  for pc = 1, info.bytecodes - 1 do
    local ins = util.funcbc(fn, pc)
    if bit.band(ins, 255) == globalRead then
      seen[util.funck(fn, -bit.rshift(ins, 16) - 1)] = true
    end
  end
  for i = 0, info.gcconsts - 1 do
    local child = util.funck(fn, -i - 1)
    if type(child) == 'proto' then globalReads(child, seen) end
  end
end
local probe = {}
globalReads(assert(loadstring('local function f() return scope_probe end; local scope_probe = 1; return f')), probe)
T.check(probe.scope_probe, 'nested prototypes include reads before a local declaration')

local bad = {}
for _, f in ipairs(files) do
  local file = assert(io.open(f))
  local src = file:read('*a')
  file:close()
  local seen = {}
  globalReads(assert(loadfile(f)), seen)
  for g in pairs(seen) do
      if src:find('\n%s*local%s+' .. g .. '%f[^%w_]') or src:find('\n%s*local%s+function%s+' .. g .. '%f[^%w_]')
          or src:find('\n%s*local%s+[%w_,%s]-,%s*' .. g .. '%f[^%w_]') then
        bad[#bad + 1] = f:gsub('\\', '/'):match('lua/(.*)$') .. ': ' .. g
      end
  end
end
T.check(#bad == 0, 'no global reads of a file\'s own locals: ' .. table.concat(bad, ', '))
T.done('test_scoping')
