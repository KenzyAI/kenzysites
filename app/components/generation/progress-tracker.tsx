"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Progress } from '@/components/ui/progress';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Loader2, 
  CheckCircle, 
  Circle, 
  Sparkles,
  Brain,
  Palette,
  Code,
  Zap,
  Clock,
  Star
} from 'lucide-react';

interface ProgressStep {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  estimatedDuration: number; // in milliseconds
}

interface ProgressTrackerProps {
  isGenerating: boolean;
  onComplete?: () => void;
  businessInfo?: {
    name: string;
    industry: string;
    description: string;
  };
}

const GENERATION_STEPS: ProgressStep[] = [
  {
    id: 'analyze',
    label: 'Analisando Negócio',
    description: 'Compreendendo suas necessidades e objetivos',
    icon: Brain,
    estimatedDuration: 3000,
  },
  {
    id: 'research',
    label: 'Pesquisa de Mercado',
    description: 'Analisando tendências do seu setor',
    icon: Sparkles,
    estimatedDuration: 4000,
  },
  {
    id: 'design',
    label: 'Criando Designs',
    description: 'Gerando paletas de cores e tipografias',
    icon: Palette,
    estimatedDuration: 5000,
  },
  {
    id: 'content',
    label: 'Personalizando Conteúdo',
    description: 'Criando textos únicos para seu negócio',
    icon: Code,
    estimatedDuration: 4500,
  },
  {
    id: 'optimize',
    label: 'Otimizando Performance',
    description: 'Configurando SEO e responsividade',
    icon: Zap,
    estimatedDuration: 3500,
  },
];

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ 
  isGenerating, 
  onComplete,
  businessInfo
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (!isGenerating) {
      // Reset when not generating
      setCurrentStep(0);
      setCompletedSteps([]);
      setOverallProgress(0);
      setIsComplete(false);
      setElapsedTime(0);
      return;
    }

    // Start the generation process
    let totalTime = 0;
    const totalDuration = GENERATION_STEPS.reduce((acc, step) => acc + step.estimatedDuration, 0);
    
    const processSteps = async () => {
      for (let i = 0; i < GENERATION_STEPS.length; i++) {
        const step = GENERATION_STEPS[i];
        setCurrentStep(i);
        
        // Animate progress for current step
        const stepProgress = new Promise<void>((resolve) => {
          const stepStart = Date.now();
          const interval = setInterval(() => {
            const elapsed = Date.now() - stepStart;
            const stepProgressPercent = Math.min(elapsed / step.estimatedDuration, 1);
            const newOverallProgress = ((totalTime + (elapsed * stepProgressPercent)) / totalDuration) * 100;
            
            setOverallProgress(Math.min(newOverallProgress, 100));
            
            if (elapsed >= step.estimatedDuration) {
              clearInterval(interval);
              setCompletedSteps(prev => [...prev, step.id]);
              totalTime += step.estimatedDuration;
              resolve();
            }
          }, 100);
        });

        await stepProgress;
      }

      // Complete the process
      setTimeout(() => {
        setIsComplete(true);
        setOverallProgress(100);
        if (onComplete) {
          onComplete();
        }
      }, 500);
    };

    processSteps();

    // Timer for elapsed time
    const timeInterval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timeInterval);
  }, [isGenerating, onComplete]);

  const formatTime = (seconds: number) => {
    return `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`;
  };

  if (!isGenerating) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <Card className="w-full max-w-2xl mx-4 p-8">
        <div className="text-center mb-8">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="inline-block mb-4"
          >
            <Sparkles className="w-12 h-12 text-primary" />
          </motion.div>
          
          <h2 className="text-2xl font-bold mb-2">
            {isComplete ? '🎉 Site Gerado com Sucesso!' : 'Criando Seu Site Personalizado'}
          </h2>
          
          {businessInfo && (
            <p className="text-muted-foreground mb-4">
              Gerando variações para <strong>{businessInfo.name}</strong> - {businessInfo.industry}
            </p>
          )}

          <div className="flex items-center justify-center gap-4 mb-6">
            <Badge variant="secondary" className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              {formatTime(elapsedTime)}
            </Badge>
            <Badge variant="outline" className="flex items-center gap-2">
              <Star className="w-4 h-4" />
              IA Generativa
            </Badge>
          </div>

          {/* Overall Progress */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Progresso Geral</span>
              <span className="text-sm text-muted-foreground">
                {Math.round(overallProgress)}%
              </span>
            </div>
            <Progress value={overallProgress} className="h-3" />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-4">
          {GENERATION_STEPS.map((step, index) => {
            const isCompleted = completedSteps.includes(step.id);
            const isCurrent = currentStep === index && !isCompleted;
            const isUpcoming = index > currentStep;
            
            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center gap-4 p-4 rounded-lg border transition-all ${
                  isCompleted 
                    ? 'bg-green-50 border-green-200 text-green-800' 
                    : isCurrent 
                      ? 'bg-blue-50 border-blue-200 text-blue-800' 
                      : 'bg-gray-50 border-gray-200 text-gray-600'
                }`}
              >
                <div className="flex-shrink-0">
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : isCurrent ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 className="w-6 h-6 text-blue-600" />
                    </motion.div>
                  ) : (
                    <Circle className="w-6 h-6 text-gray-400" />
                  )}
                </div>

                <div className="flex items-center gap-3 flex-1">
                  <step.icon className="w-5 h-5" />
                  <div>
                    <div className="font-medium">{step.label}</div>
                    <div className="text-sm opacity-80">{step.description}</div>
                  </div>
                </div>

                {isCurrent && (
                  <div className="flex-shrink-0">
                    <div className="w-6 h-6 relative">
                      <motion.div
                        className="w-full h-full border-2 border-current border-t-transparent rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      />
                    </div>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>

        {isComplete && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center mt-8 p-6 bg-green-50 rounded-lg border border-green-200"
          >
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-green-800 mb-2">
              Processo Concluído!
            </h3>
            <p className="text-green-600 mb-4">
              5 variações únicas foram criadas para seu negócio
            </p>
            <p className="text-sm text-green-700">
              Tempo total: {formatTime(elapsedTime)} | Velocidade: ⚡ Ultra Rápido
            </p>
          </motion.div>
        )}
      </Card>
    </motion.div>
  );
};

export default ProgressTracker;