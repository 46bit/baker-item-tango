#!/usr/bin/env ruby

require "json"

=begin
while line = $stdin.read
  puts line
  m = line.match /bitLearned won! (.*)/
  puts m
  next if m.nil?
  puts JSON.parse(m[2]).length
end
=end

output = []
r, io = IO.pipe
fork do
  system("python", "battleships_text.py", out: io, err: :out)
end
io.close

r.each_line do |line|
  puts line
  m = line.match /bitLearned won! (.*)/
  puts m
  next if m.nil?
  puts JSON.parse(m[2]).length
end
