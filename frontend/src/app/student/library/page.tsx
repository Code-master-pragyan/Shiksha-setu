"use client";

import { useState } from "react";
import { Search, BookOpen, FileText, Info } from "lucide-react";
import { searchRetrieval } from "@/lib/api/retrieval";
import { RetrievalResult } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function LibraryPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<RetrievalResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [expandedChunks, setExpandedChunks] = useState<Record<string, boolean>>({});

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setResults([]);

    try {
      // Use student's profile information if available, else omit (backend handles defaults or allows any)
      const response = await searchRetrieval({
        query: query.trim(),
        top_k: 5,
      });
      setResults(response.results || []);
    } catch (err: unknown) {
      console.error("Search error:", err);
      const errorMessage = err instanceof Error ? err.message : "An error occurred while searching the library. Please try again.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpand = (chunkId: string) => {
    setExpandedChunks(prev => ({
      ...prev,
      [chunkId]: !prev[chunkId]
    }));
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8 pb-20 animate-in fade-in duration-500">
      <div className="space-y-4 text-center">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Textbook Library</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Search the verified educational knowledge base. 
          Enter your question or keywords to find relevant textbook excerpts.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 max-w-2xl mx-auto">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="e.g. What is a cell?"
            className="flex h-11 w-full rounded-md border border-input bg-background px-10 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
          />
        </div>
        <Button type="submit" size="lg" disabled={isLoading || !query.trim()}>
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </form>

      {error && (
        <div className="bg-destructive/15 text-destructive p-4 rounded-lg flex items-start gap-3">
          <Info className="h-5 w-5 mt-0.5 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {hasSearched && !isLoading && !error && (
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b pb-4">
            <h2 className="text-xl font-semibold">Search Results</h2>
            <Badge variant="secondary">{results.length} result{results.length !== 1 ? 's' : ''}</Badge>
          </div>

          {results.length === 0 ? (
            <div className="text-center py-12 bg-muted/30 rounded-lg border border-dashed">
              <BookOpen className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium mb-1">No relevant textbook material found</h3>
              <p className="text-muted-foreground">Try a different question or keywords.</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {results.map((result) => {
                const isExpanded = expandedChunks[result.chunk_id];
                const needsTruncation = result.text.length > 300;
                
                return (
                  <Card key={result.chunk_id} className="overflow-hidden">
                    <CardHeader className="bg-muted/30 border-b pb-4">
                      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                        <div>
                          <CardTitle className="text-lg flex items-center gap-2">
                            <FileText className="h-5 w-5 text-primary" />
                            {result.title}
                          </CardTitle>
                          <CardDescription className="mt-2 space-y-1 text-sm">
                            {result.chapter && (
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-foreground/80">Chapter:</span>
                                {result.chapter_number ? `${result.chapter_number} - ` : ''}
                                {result.chapter}
                              </div>
                            )}
                            {result.section && (
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-foreground/80">Section:</span>
                                {result.section}
                              </div>
                            )}
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-foreground/80">Pages:</span>
                              {result.page_start}{result.page_end !== result.page_start ? `–${result.page_end}` : ''}
                            </div>
                          </CardDescription>
                        </div>
                        <div className="flex flex-wrap gap-2 justify-start md:justify-end">
                          <Badge variant="outline">{result.subject}</Badge>
                          <Badge variant="outline">Grade {result.grade}</Badge>
                          <Badge variant="outline" className="text-xs">
                            Score: {(result.similarity_score * 100).toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4 text-base leading-relaxed text-foreground/90 whitespace-pre-wrap">
                      <div className="relative">
                        <div className={!isExpanded && needsTruncation ? "line-clamp-4" : ""}>
                          {result.text}
                        </div>
                        {!isExpanded && needsTruncation && (
                          <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-background to-transparent" />
                        )}
                      </div>
                    </CardContent>
                    {needsTruncation && (
                      <CardFooter className="pt-0 pb-4">
                        <Button 
                          type="button"
                          variant="ghost" 
                          size="sm" 
                          onClick={() => toggleExpand(result.chunk_id)}
                          className="w-full text-primary"
                        >
                          {isExpanded ? "Show less" : "Read full excerpt"}
                        </Button>
                      </CardFooter>
                    )}
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}

      {isLoading && (
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b pb-4">
            <div className="h-7 w-32 bg-muted rounded animate-pulse"></div>
          </div>
          <div className="grid gap-6">
            {[1, 2, 3].map(i => (
              <Card key={i} className="overflow-hidden">
                <CardHeader className="bg-muted/30 border-b">
                  <div className="h-6 w-3/4 bg-muted rounded animate-pulse mb-2"></div>
                  <div className="h-4 w-1/2 bg-muted rounded animate-pulse"></div>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="space-y-2">
                    <div className="h-4 w-full bg-muted rounded animate-pulse"></div>
                    <div className="h-4 w-full bg-muted rounded animate-pulse"></div>
                    <div className="h-4 w-3/4 bg-muted rounded animate-pulse"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
