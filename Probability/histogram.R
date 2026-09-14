num <- readLines("C:/Users/USER/Documents/Code/B26/Probability/iota.txt")

digits <- unlist(regmatches(num, gregexpr("[0-9]", num)))

freq <- table(factor(digits, levels = 0:9))

barplot(freq,
        xlab = "Dígito",
        ylab = "Frecuencia",
        main = "Frecuencias por dígito en Iota",
        col = "red")